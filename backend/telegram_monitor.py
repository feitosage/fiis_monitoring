"""
Script de monitoramento de FIIs com notificações no Telegram
Executa análises periódicas e envia alertas sobre variações significativas
"""
import yfinance as yf
import schedule
import time
from datetime import datetime, time as dt_time
from telegram_notifier import TelegramNotifier, run_async
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Lista de FIIs para monitorar (mesma lista do app.py)
FIIS_POPULARES = [
    'MXRF11.SA', 'MCRE11.SA', 'VGHF11.SA', 'VISC11.SA',
    'RURA11.SA', 'TRXF11.SA', 'XPLG11.SA', 'RZTR11.SA',
    'CPTS11.SA', 'HSML11.SA', 'PVBI11.SA', 'OUJP11.SA',
    'VILG11.SA', 'VRTA11.SA', 'HGRU11.SA', 'RBRP11.SA'
]

# Configurações de alertas
ALERTA_ALTA_MINIMA = float(os.getenv('ALERTA_ALTA_MINIMA', '1.5'))  # % mínima para alertar alta
ALERTA_BAIXA_MINIMA = float(os.getenv('ALERTA_BAIXA_MINIMA', '-1.5'))  # % mínima para alertar baixa
ALERTA_DESCONTO_PVP = float(os.getenv('ALERTA_DESCONTO_PVP', '0.95'))  # P/VP mínimo para alertar desconto

# Configurações de horário de pregão (segunda a sexta, 10h-17h)
HORA_INICIO_PREGAO = 10
HORA_FIM_PREGAO = 17


def buscar_dados_fii(ticker):
    """
    Busca dados atualizados de um FII
    
    Args:
        ticker (str): Ticker do FII
    
    Returns:
        dict: Dados do FII ou None se houver erro
    """
    try:
        fii = yf.Ticker(ticker)
        
        # Busca histórico para calcular variação
        hist = fii.history(period='5d')
        
        if hist.empty or len(hist) < 2:
            print(f"  ⚠️  {ticker}: Sem dados suficientes")
            return None
        
        info = fii.info if fii.info else {}
        
        # Preço atual
        preco_atual = info.get('currentPrice') or info.get('regularMarketPrice')
        if not preco_atual:
            preco_atual = float(hist['Close'].iloc[-1])
        
        # Calcula variação do dia
        preco_hoje = float(hist['Close'].iloc[-1])
        preco_ontem = float(hist['Close'].iloc[-2])
        variacao_dia = ((preco_hoje - preco_ontem) / preco_ontem) * 100
        
        # P/VP
        pvp = info.get('priceToBook', 0)
        if not pvp or pvp == 0:
            book_value = info.get('bookValue', 0)
            if book_value and book_value > 0:
                pvp = preco_atual / book_value
        
        # Valida P/VP
        if pvp and (pvp < 0.3 or pvp > 3.0):
            pvp = None
        
        # Dividend Yield
        dy = info.get('dividendYield', 0)
        if dy:
            if dy > 100:
                dy = dy / 100
            elif dy > 1:
                pass
            elif dy > 0.01:
                dy = dy * 100
            
            if dy < 0 or dy > 30:
                dy = 0
        
        # Volume
        volume = int(hist['Volume'].iloc[-1]) if not hist.empty else 0
        
        return {
            'ticker': ticker,
            'nome': info.get('longName', ticker.replace('.SA', '')),
            'preco': preco_atual,
            'variacao': variacao_dia,
            'pvp': pvp,
            'dy': dy,
            'volume': volume
        }
        
    except Exception as e:
        print(f"  ❌ Erro ao buscar {ticker}: {str(e)}")
        return None


def analisar_fiis():
    """
    Analisa todos os FIIs e retorna dados organizados
    
    Returns:
        dict: Dados organizados com 'todos', 'altas' e 'baixas'
    """
    print(f"\n{'='*60}")
    print(f"📊 Iniciando análise de FIIs - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    dados_fiis = []
    
    for ticker in FIIS_POPULARES:
        print(f"🔍 Buscando {ticker}...")
        dados = buscar_dados_fii(ticker)
        
        if dados:
            dados_fiis.append(dados)
            print(f"  ✅ {ticker}: R$ {dados['preco']:.2f} ({dados['variacao']:+.2f}%)")
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.5)
    
    # Ordena por variação
    dados_fiis_ordenados = sorted(dados_fiis, key=lambda x: x['variacao'], reverse=True)
    
    # Separa altas e baixas
    maiores_altas = [f for f in dados_fiis_ordenados if f['variacao'] > 0]
    maiores_baixas = sorted([f for f in dados_fiis if f['variacao'] < 0], key=lambda x: x['variacao'])
    
    print(f"\n{'='*60}")
    print(f"✅ Análise concluída!")
    print(f"  • Total analisado: {len(dados_fiis)} FIIs")
    print(f"  • Em alta: {len(maiores_altas)}")
    print(f"  • Em baixa: {len(maiores_baixas)}")
    print(f"{'='*60}\n")
    
    return {
        'todos': dados_fiis,
        'altas': maiores_altas,
        'baixas': maiores_baixas
    }


def enviar_alerta_resumo():
    """
    Executa a análise e envia alerta resumido no Telegram
    """
    try:
        # Analisa FIIs
        dados = analisar_fiis()
        
        if not dados['todos']:
            print("❌ Nenhum dado disponível para enviar alerta")
            return
        
        # Envia notificação
        print("📱 Enviando notificação no Telegram...")
        
        notifier = TelegramNotifier()
        sucesso = run_async(notifier.enviar_alerta_resumo(dados, len(FIIS_POPULARES)))
        
        if sucesso:
            print("✅ Alerta enviado com sucesso!")
        else:
            print("❌ Falha ao enviar alerta")
            
    except Exception as e:
        print(f"❌ Erro ao enviar alerta: {str(e)}")


def enviar_alertas_personalizados():
    """
    Analisa FIIs e envia alertas personalizados para variações significativas
    """
    try:
        # Analisa FIIs
        dados = analisar_fiis()
        
        if not dados['todos']:
            print("❌ Nenhum dado disponível")
            return
        
        notifier = TelegramNotifier()
        alertas_enviados = 0
        
        # Alertas de altas significativas
        for fii in dados['altas']:
            if fii['variacao'] >= ALERTA_ALTA_MINIMA:
                print(f"🚀 Alerta de ALTA: {fii['ticker']} ({fii['variacao']:+.2f}%)")
                sucesso = run_async(
                    notifier.enviar_alerta_personalizado(fii['ticker'], fii, 'alta')
                )
                if sucesso:
                    alertas_enviados += 1
                time.sleep(1)  # Pausa entre mensagens
        
        # Alertas de baixas significativas
        for fii in dados['baixas']:
            if fii['variacao'] <= ALERTA_BAIXA_MINIMA:
                print(f"⚠️ Alerta de BAIXA: {fii['ticker']} ({fii['variacao']:+.2f}%)")
                sucesso = run_async(
                    notifier.enviar_alerta_personalizado(fii['ticker'], fii, 'baixa')
                )
                if sucesso:
                    alertas_enviados += 1
                time.sleep(1)
        
        # Alertas de descontos (P/VP < threshold)
        for fii in dados['todos']:
            if fii.get('pvp') and fii['pvp'] < ALERTA_DESCONTO_PVP:
                print(f"💎 Alerta de DESCONTO: {fii['ticker']} (P/VP: {fii['pvp']:.2f})")
                sucesso = run_async(
                    notifier.enviar_alerta_personalizado(fii['ticker'], fii, 'desconto')
                )
                if sucesso:
                    alertas_enviados += 1
                time.sleep(1)
        
        print(f"\n✅ {alertas_enviados} alertas personalizados enviados")
        
    except Exception as e:
        print(f"❌ Erro ao enviar alertas personalizados: {str(e)}")


def esta_em_horario_pregao():
    """
    Verifica se está no horário de pregão (segunda a sexta, 10h-17h)
    
    Returns:
        bool: True se está no horário de pregão
    """
    agora = datetime.now()
    
    # Verifica se é dia da semana (0=segunda, 6=domingo)
    if agora.weekday() >= 5:  # 5=sábado, 6=domingo
        return False
    
    # Verifica horário (10h às 17h)
    hora_atual = agora.hour
    if hora_atual < HORA_INICIO_PREGAO or hora_atual >= HORA_FIM_PREGAO:
        return False
    
    return True


def executar_monitoramento():
    """
    Executa o monitoramento completo (resumo + alertas personalizados)
    Só executa se estiver no horário de pregão
    """
    print(f"\n{'█'*60}")
    print(f"🤖 MONITORAMENTO DE FIIs - INICIADO")
    print(f"{'█'*60}\n")
    
    # Verifica horário de pregão
    if not esta_em_horario_pregao():
        agora = datetime.now()
        dia_semana = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo'][agora.weekday()]
        
        print(f"⏸️  FORA DO HORÁRIO DE PREGÃO")
        print(f"  • Dia: {dia_semana.capitalize()}")
        print(f"  • Hora: {agora.strftime('%H:%M')}")
        print(f"  • Pregão: Segunda a Sexta, 10h-17h")
        print(f"\n⏰ Próxima verificação em 30 minutos")
        print(f"{'█'*60}\n")
        return
    
    # Envia alerta resumido
    enviar_alerta_resumo()
    
    # Opcional: Descomentar para enviar alertas personalizados também
    # print("\n" + "─"*60 + "\n")
    # enviar_alertas_personalizados()
    
    print(f"\n{'█'*60}")
    print(f"✅ MONITORAMENTO CONCLUÍDO")
    print(f"⏰ Próxima execução em 30 minutos")
    print(f"{'█'*60}\n")


def iniciar_monitoramento_agendado(intervalo_horas=0.5):
    """
    Inicia o monitoramento agendado
    
    Args:
        intervalo_horas (int): Intervalo em horas entre cada execução
    """
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        🤖 BOT DE MONITORAMENTO DE FIIs - TELEGRAM 🤖      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

⚙️  CONFIGURAÇÕES:
  • FIIs monitorados: {len(FIIS_POPULARES)}
  • Intervalo: A cada {intervalo_horas} hora(s)
  • Horário: Segunda a Sexta, {HORA_INICIO_PREGAO}h-{HORA_FIM_PREGAO}h
  • Alerta alta: ≥ {ALERTA_ALTA_MINIMA:+.2f}%
  • Alerta baixa: ≤ {ALERTA_BAIXA_MINIMA:+.2f}%
  • Alerta desconto P/VP: < {ALERTA_DESCONTO_PVP:.2f}

🔄 Testando conexão com Telegram...
""")
    
    # Testa conexão
    try:
        notifier = TelegramNotifier()
        if run_async(notifier.testar_conexao()):
            print("✅ Conexão com Telegram estabelecida!\n")
        else:
            print("❌ Falha na conexão com Telegram!")
            return
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return
    
    # Executa imediatamente a primeira análise
    print("🚀 Executando primeira análise...\n")
    executar_monitoramento()
    
    # Agenda execuções futuras
    schedule.every(intervalo_horas).hours.do(executar_monitoramento)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  ✅ BOT ATIVO - Monitoramento em andamento...             ║
║                                                            ║
║  ⏰ Próxima atualização: {(datetime.now().replace(microsecond=0) + __import__('datetime').timedelta(hours=intervalo_horas)).strftime('%d/%m/%Y %H:%M:%S')}      ║
║                                                            ║
║  💡 Pressione Ctrl+C para parar                           ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Loop principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print("🛑 Monitoramento interrompido pelo usuário")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor de FIIs com notificações no Telegram')
    parser.add_argument(
        '--intervalo',
        type=float,
        default=0.5,
        help='Intervalo em horas entre cada atualização (padrão: 0.5)'
    )
    parser.add_argument(
        '--teste',
        action='store_true',
        help='Executa apenas uma análise de teste e sai'
    )
    
    args = parser.parse_args()
    
    if args.teste:
        print("\n🧪 MODO TESTE - Executando análise única...\n")
        executar_monitoramento()
    else:
        iniciar_monitoramento_agendado(args.intervalo)

