"""
Script de teste para enviar notificação AGORA (ignora horário de pregão)
"""
import yfinance as yf
import time
from datetime import datetime
from telegram_notifier import TelegramNotifier, run_async

# Lista de FIIs para monitorar
FIIS_POPULARES = [
    'MXRF11.SA', 'MCRE11.SA', 'VGHF11.SA', 'VISC11.SA',
    'RURA11.SA', 'TRXF11.SA', 'XPLG11.SA', 'RZTR11.SA',
    'CPTS11.SA', 'HSML11.SA', 'PVBI11.SA', 'OUJP11.SA',
    'VILG11.SA', 'VRTA11.SA', 'HGRU11.SA', 'RBRP11.SA'
]

print("╔════════════════════════════════════════════════════════════╗")
print("║                                                            ║")
print("║           🧪 TESTE DE NOTIFICAÇÃO - FIIs 🧪               ║")
print("║                                                            ║")
print("╚════════════════════════════════════════════════════════════╝")
print()
print("📊 Buscando dados atualizados dos FIIs...")
print("⏳ Isso pode levar alguns segundos...")
print()

def buscar_dados_fii(ticker):
    """Busca dados atualizados de um FII"""
    try:
        fii = yf.Ticker(ticker)
        hist = fii.history(period='5d')
        
        if hist.empty or len(hist) < 2:
            return None
        
        info = fii.info if fii.info else {}
        
        # Preço atual
        preco_atual = info.get('currentPrice') or info.get('regularMarketPrice')
        if not preco_atual:
            preco_atual = float(hist['Close'].iloc[-1])
        
        # Variação
        preco_hoje = float(hist['Close'].iloc[-1])
        preco_ontem = float(hist['Close'].iloc[-2])
        variacao_dia = ((preco_hoje - preco_ontem) / preco_ontem) * 100
        
        # P/VP
        pvp = info.get('priceToBook', 0)
        if not pvp or pvp == 0:
            book_value = info.get('bookValue', 0)
            if book_value and book_value > 0:
                pvp = preco_atual / book_value
        
        if pvp and (pvp < 0.3 or pvp > 3.0):
            pvp = None
        
        # DY
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
        print(f"  ⚠️  Erro em {ticker}: {str(e)}")
        return None

# Busca dados
dados_fiis = []
for i, ticker in enumerate(FIIS_POPULARES, 1):
    print(f"  [{i:2d}/{len(FIIS_POPULARES)}] {ticker}...", end=' ')
    dados = buscar_dados_fii(ticker)
    
    if dados:
        dados_fiis.append(dados)
        print(f"✓ R$ {dados['preco']:.2f} ({dados['variacao']:+.2f}%)")
    else:
        print("✗")
    
    time.sleep(0.3)  # Pausa para não sobrecarregar

print()
print(f"✅ {len(dados_fiis)} FIIs analisados com sucesso!")
print()

# Organiza dados
dados_ordenados = sorted(dados_fiis, key=lambda x: x['variacao'], reverse=True)
maiores_altas = [f for f in dados_ordenados if f['variacao'] > 0]
maiores_baixas = sorted([f for f in dados_fiis if f['variacao'] < 0], key=lambda x: x['variacao'])

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 RESUMO:")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"  • Em alta: {len(maiores_altas)}")
print(f"  • Em baixa: {len(maiores_baixas)}")
print(f"  • Estável: {len(dados_fiis) - len(maiores_altas) - len(maiores_baixas)}")
print()

# Envia notificação
print("📱 Enviando notificação no Telegram...")
print()

try:
    notifier = TelegramNotifier()
    
    dados = {
        'todos': dados_fiis,
        'altas': maiores_altas,
        'baixas': maiores_baixas
    }
    
    sucesso = run_async(notifier.enviar_alerta_resumo(dados, len(FIIS_POPULARES)))
    
    if sucesso:
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                            ║")
        print("║               ✅ NOTIFICAÇÃO ENVIADA! ✅                  ║")
        print("║                                                            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print("📱 Verifique seu Telegram!")
        print()
    else:
        print("❌ Falha ao enviar notificação")
        
except Exception as e:
    print(f"❌ Erro: {str(e)}")

