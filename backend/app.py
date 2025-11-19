from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import time
from dados_mock import FIIS_MOCK, get_fii_mock_details, get_dividendos_mock
from dotenv import load_dotenv
import os
from openai import OpenAI
from setores_fiis import get_setor_info, CARACTERISTICAS_SETORES
from pesquisa_fiis import pesquisador, pesquisar_multiplos_fiis

# Carrega variáveis de ambiente
load_dotenv()

# Modo de demonstração (use dados mock quando Yahoo Finance estiver indisponível)
MODO_DEMO = False  # True = usa dados mock, False = busca Yahoo Finance real

app = Flask(__name__)
CORS(app)

# Inicializa cliente OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# Lista de FIIs para análise no Painel Geral
FIIS_POPULARES = [
    'MXRF11.SA', 'MCRE11.SA', 'VGHF11.SA', 'VISC11.SA',
    'RURA11.SA', 'TRXF11.SA', 'XPLG11.SA', 'RZTR11.SA',
    'CPTS11.SA', 'HSML11.SA', 'PVBI11.SA', 'OUJP11.SA',
    'VILG11.SA', 'VRTA11.SA', 'HGRU11.SA', 'RBRP11.SA'
]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({'status': 'ok', 'message': 'API está funcionando'})

@app.route('/api/fii/<ticker>', methods=['GET'])
def get_fii_info(ticker):
    """Busca informações detalhadas de um FII específico"""
    try:
        # Adiciona .SA se não estiver presente
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        # Se em modo demo, retorna dados mock
        if MODO_DEMO:
            print(f"⚠️  MODO DEMO: Retornando dados de exemplo para {ticker}")
            return jsonify(get_fii_mock_details(ticker))
        
        fii = yf.Ticker(ticker)
        
        # Busca histórico dos últimos 3 meses para ter mais dados de volume
        try:
            hist = fii.history(period='3mo')
            
            if hist.empty:
                return jsonify({'erro': f'FII {ticker} não possui dados disponíveis'}), 404
        except Exception as hist_error:
            print(f"Erro ao buscar histórico de {ticker}: {str(hist_error)}")
            return jsonify({'erro': f'Erro ao buscar dados de {ticker}'}), 500
        
        info = fii.info if fii.info else {}
        
        # Busca preço do último fechamento se não houver currentPrice
        preco_atual = info.get('currentPrice') or info.get('regularMarketPrice')
        if not preco_atual and not hist.empty:
            preco_atual = float(hist['Close'].iloc[-1])
        
        # Busca e valida Dividend Yield
        dy = info.get('dividendYield', 0)
        
        # Yahoo Finance inconsistente com DY
        if dy:
            if dy > 100:  # Absurdo: 955 → 9.55
                dy = dy / 100
            elif dy > 1:  # Já é %: 12.45 → mantém
                pass
            elif dy > 0.01:  # Decimal: 0.1245 → 12.45
                dy = dy * 100
            
            # Valida range (0% a 30%)
            if dy < 0 or dy > 30:
                dy = 0
        
        # Calcula variação do dia MANUALMENTE (Yahoo Finance não é confiável para FIIs .SA)
        # Compara fechamento de hoje vs ontem
        variacao_dia = 0
        if not hist.empty and len(hist) >= 2:
            try:
                preco_hoje = float(hist['Close'].iloc[-1])
                preco_ontem = float(hist['Close'].iloc[-2])
                variacao_dia = (preco_hoje - preco_ontem) / preco_ontem
                print(f"  ✅ Variação calculada: {preco_ontem:.2f} → {preco_hoje:.2f} = {variacao_dia*100:.2f}%")
            except Exception as e:
                print(f"  ⚠️  Erro ao calcular variação: {str(e)}")
                variacao_dia = 0
        else:
            print(f"  ⚠️  Histórico insuficiente para calcular variação")
        
        # Busca volume - sempre pega o último registro com volume > 0
        volume_atual = 0
        periodo_volume = 'Sem dados'
        
        if not hist.empty:
            # Percorre do mais recente para o mais antigo
            for i in range(len(hist) - 1, -1, -1):
                vol = int(hist['Volume'].iloc[i])
                if vol > 0:
                    volume_atual = vol
                    data_vol = hist.index[i]
                    
                    # Verifica se é hoje
                    from datetime import date
                    hoje = date.today()
                    data_registro = data_vol.date() if hasattr(data_vol, 'date') else data_vol.to_pydatetime().date()
                    
                    if data_registro == hoje:
                        periodo_volume = 'hoje'
                    else:
                        periodo_volume = data_vol.strftime('%d/%m/%Y')
                    break
        
        response = {
            'ticker': ticker,
            'nome': info.get('longName', ticker.replace('.SA', '')),
            'preco_atual': preco_atual or 0,
            'variacao_dia': variacao_dia,
            'dividend_yield': dy,
            'volume': volume_atual,
            'volume_data': periodo_volume,
            'minima_52_semanas': info.get('fiftyTwoWeekLow', float(hist['Low'].min()) if not hist.empty else 0),
            'maxima_52_semanas': info.get('fiftyTwoWeekHigh', float(hist['High'].max()) if not hist.empty else 0),
            'historico': [
                {
                    'data': index.strftime('%Y-%m-%d'),
                    'fechamento': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                for index, row in hist.iterrows()
            ]
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Erro ao buscar FII {ticker}: {str(e)}")
        return jsonify({'erro': f'Erro ao processar dados de {ticker}'}), 500

@app.route('/api/fiis', methods=['GET'])
def get_multiple_fiis():
    """Busca informações de múltiplos FIIs"""
    try:
        # Se em modo demo, retorna dados mock
        if MODO_DEMO:
            print("⚠️  MODO DEMO: Usando dados de exemplo")
            return jsonify({
                'fiis': FIIS_MOCK,
                'ultima_atualizacao': datetime.now().isoformat(),
                'total': len(FIIS_MOCK)
            })
        
        tickers = request.args.get('tickers', '')
        
        if not tickers:
            tickers = ','.join(FIIS_POPULARES)
        
        ticker_list = [t.strip() for t in tickers.split(',')]
        results = []
        
        for ticker in ticker_list:
            if not ticker.endswith('.SA'):
                ticker = f"{ticker}.SA"
            
            try:
                fii = yf.Ticker(ticker)
                
                # Tenta buscar histórico para verificar se tem dados
                hist = fii.history(period='5d')
                if hist.empty:
                    print(f"FII {ticker} sem dados disponíveis, pulando...")
                    continue
                
                info = fii.info if fii.info else {}
                
                # Busca preço do último fechamento se não houver currentPrice
                preco_atual = info.get('currentPrice') or info.get('regularMarketPrice')
                if not preco_atual:
                    preco_atual = float(hist['Close'].iloc[-1])
                
                # Busca P/VP (priceToBook)
                pvp = info.get('priceToBook', 0)
                
                # Se não tiver P/VP no info, tenta calcular manualmente
                if not pvp or pvp == 0:
                    book_value = info.get('bookValue', 0)
                    if book_value and book_value > 0:
                        pvp = preco_atual / book_value
                
                # Valida e sanitiza P/VP (valores razoáveis: 0.5 a 2.0)
                if pvp and (pvp < 0.3 or pvp > 3.0):
                    pvp = None
                
                # Busca e valida Dividend Yield
                dy = info.get('dividendYield', 0)
                
                # Yahoo Finance inconsistente: às vezes retorna decimal (0.12 = 12%), às vezes percentual (12)
                # Validação: DY razoável para FIIs é 0% a 30%
                if dy:
                    if dy > 100:  # Se vier como 1200 (absurdo), divide por 100
                        dy = dy / 100
                    if dy > 1:  # Se vier como 12.45 (já é %), mantém
                        pass
                    elif dy > 0.01:  # Se vier como 0.1245 (decimal), converte para %
                        dy = dy * 100
                    
                    # Valida range razoável (0% a 30%)
                    if dy < 0 or dy > 30:
                        dy = 0
                
                # Busca volume
                volume = int(hist['Volume'].iloc[-1]) if not hist.empty else 0
                
                # Calcula variação do dia MANUALMENTE (Yahoo Finance não é confiável para FIIs .SA)
                variacao_dia = 0
                if not hist.empty and len(hist) >= 2:
                    try:
                        preco_hoje = float(hist['Close'].iloc[-1])
                        preco_ontem = float(hist['Close'].iloc[-2])
                        variacao_dia = (preco_hoje - preco_ontem) / preco_ontem
                    except:
                        variacao_dia = 0
                
                results.append({
                    'ticker': ticker,
                    'nome': info.get('longName', ticker.replace('.SA', '')),
                    'preco_atual': preco_atual or 0,
                    'variacao_dia': variacao_dia,
                    'dividend_yield': dy,
                    'volume': volume,
                    'pvp': pvp if pvp else None
                })
            except Exception as e:
                print(f"Erro ao buscar {ticker}: {str(e)}")
                continue
        
        # Retorna dados com timestamp
        return jsonify({
            'fiis': results,
            'ultima_atualizacao': datetime.now().isoformat(),
            'total': len(results)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_fii():
    """Busca um FII pelo ticker"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'erro': 'Parâmetro q é obrigatório'}), 400
    
    try:
        ticker = query.upper()
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        # Se em modo demo, verifica se ticker existe na lista
        if MODO_DEMO:
            print(f"⚠️  MODO DEMO: Verificando {ticker}")
            # Verifica se está na lista de FIIs populares ou mock
            if ticker in FIIS_POPULARES or ticker.replace('.SA', '') in [f.replace('.SA', '') for f in FIIS_POPULARES]:
                return jsonify({
                    'ticker': ticker,
                    'nome': ticker.replace('.SA', ''),
                    'existe': True
                })
            else:
                return jsonify({'erro': f'FII {ticker} não encontrado na base de dados demo'}), 404
        
        # Modo real - busca no Yahoo Finance
        print(f"🔍 Buscando dados reais para {ticker} no Yahoo Finance...")
        
        fii = yf.Ticker(ticker)
        
        # Tenta buscar dados históricos para verificar se existe
        # Usa período menor primeiro (mais rápido)
        try:
            print(f"  → Tentando período de 5 dias...")
            hist = fii.history(period='5d', timeout=10)
            
            if hist.empty:
                print(f"  → Sem dados em 5d, tentando 1 mês...")
                hist = fii.history(period='1mo', timeout=10)
                
                if hist.empty:
                    print(f"  → Sem dados em 1mo, tentando 3 meses...")
                    hist = fii.history(period='3mo', timeout=10)
                    
                    if hist.empty:
                        print(f"  ❌ Nenhum dado encontrado para {ticker}")
                        return jsonify({'erro': f'FII {ticker} não encontrado ou sem dados disponíveis no Yahoo Finance'}), 404
            
            # Se chegou aqui, encontrou dados
            print(f"  ✅ Dados encontrados para {ticker}! {len(hist)} registros")
            
            # Tenta buscar info (pode falhar, mas não é crítico)
            info = {}
            try:
                info = fii.info if hasattr(fii, 'info') and fii.info else {}
            except:
                print(f"  ⚠️  Info não disponível para {ticker}, usando dados do histórico")
            
            result = {
                'ticker': ticker,
                'nome': info.get('longName', ticker.replace('.SA', '')) if info else ticker.replace('.SA', ''),
                'existe': True
            }
            
            return jsonify(result)
            
        except Exception as hist_error:
            print(f"  ❌ Erro ao buscar histórico de {ticker}: {str(hist_error)}")
            
            # Última tentativa com período máximo e timeout maior
            try:
                print(f"  → Última tentativa com período máximo...")
                time.sleep(0.5)  # Pequena pausa
                hist = fii.history(period='max', timeout=15)
                
                if not hist.empty:
                    print(f"  ✅ Dados encontrados no período máximo!")
                    info = {}
                    try:
                        info = fii.info if hasattr(fii, 'info') and fii.info else {}
                    except:
                        pass
                    
                    return jsonify({
                        'ticker': ticker,
                        'nome': info.get('longName', ticker.replace('.SA', '')) if info else ticker.replace('.SA', ''),
                        'existe': True
                    })
            except Exception as e:
                print(f"  ❌ Falha na última tentativa: {str(e)}")
            
            # Se chegou aqui, não conseguiu buscar dados
            return jsonify({
                'erro': f'FII {ticker} não disponível no Yahoo Finance. Verifique se o ticker está correto ou tente novamente em alguns instantes.'
            }), 404
            
    except Exception as e:
        print(f"❌ Erro geral na busca de {ticker}: {str(e)}")
        return jsonify({
            'erro': f'Erro ao buscar FII. Verifique se o ticker está correto e tente novamente.'
        }), 500

@app.route('/api/fii/<ticker>/cotacoes', methods=['GET'])
def get_fii_cotacoes(ticker):
    """Busca cotações históricas de um FII (diária, mensal, anual)"""
    try:
        # Adiciona .SA se não estiver presente
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        periodo = request.args.get('periodo', '1y')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        
        print(f"📊 Buscando cotações de {ticker} para período: {periodo}")
        
        fii = yf.Ticker(ticker)
        
        # Para período de 1 dia, busca dados intradiários
        if periodo == '1d':
            print(f"  📈 Buscando dados intradiários (5 minutos)...")
            try:
                # Busca dados de 1 dia com intervalo de 5 minutos
                # Usa prepost=False para evitar dados pré/pós mercado que podem confundir
                hist = fii.history(period='1d', interval='5m', timeout=15, prepost=False)
                
                # Se não tiver dados com 5m, tenta com 1m para ter dados mais recentes
                if hist.empty:
                    print(f"  ⚠️  Sem dados em 5m, tentando intervalo de 1 minuto...")
                    hist = fii.history(period='1d', interval='1m', timeout=15, prepost=False)
            except Exception as e:
                print(f"  ❌ Erro ao buscar intradiário: {str(e)}")
                return jsonify({'erro': f'Timeout ao buscar dados intradiários. Tente novamente.'}), 500
            
            if hist.empty:
                print(f"  ❌ Nenhum dado intradiário disponível, tentando diário...")
                try:
                    hist = fii.history(period='1d', interval='1d', timeout=15)
                except Exception as e:
                    print(f"  ❌ Erro ao buscar diário: {str(e)}")
                    return jsonify({'erro': f'Timeout ao buscar dados. Tente novamente.'}), 500
            
            if hist.empty:
                print(f"  ❌ Nenhum dado disponível para {ticker}")
                # Tenta buscar pelo menos dados de 5 dias para mostrar algo
                try:
                    print(f"  → Tentando buscar últimos 5 dias como fallback...")
                    hist = fii.history(period='5d', timeout=15)
                    if hist.empty:
                        return jsonify({'erro': f'Nenhum dado disponível para {ticker}'}), 404
                    print(f"  ✅ Mostrando últimos 5 dias como fallback")
                except:
                    return jsonify({'erro': f'Nenhum dado disponível para {ticker}'}), 404
            
            print(f"  ✅ {len(hist)} registros encontrados (última atualização: {hist.index[-1].strftime('%Y-%m-%d %H:%M') if len(hist) > 0 else 'N/A'})")
            
            # Calcula estatísticas
            preco_inicial = float(hist['Close'].iloc[0])
            preco_final = float(hist['Close'].iloc[-1])
            variacao_percentual = ((preco_final - preco_inicial) / preco_inicial) * 100
            
            response = {
                'ticker': ticker,
                'periodo': periodo,
                'intradiario': True,
                'dados': [
                    {
                        'data': index.strftime('%Y-%m-%d'),
                        'hora': index.strftime('%H:%M'),
                        'timestamp': index.strftime('%Y-%m-%d %H:%M'),
                        'abertura': float(row['Open']),
                        'fechamento': float(row['Close']),
                        'maxima': float(row['High']),
                        'minima': float(row['Low']),
                        'volume': int(row['Volume'])
                    }
                    for index, row in hist.iterrows()
                ],
                'estatisticas': {
                    'preco_inicial': preco_inicial,
                    'preco_final': preco_final,
                    'preco_maximo': float(hist['High'].max()),
                    'preco_minimo': float(hist['Low'].min()),
                    'variacao_percentual': variacao_percentual,
                    'volume_medio': float(hist['Volume'].mean()),
                    'total_registros': len(hist)
                }
            }
            
            return jsonify(response)
        
        # Para outros períodos, busca dados diários normais
        # Busca histórico com timeout e forçando prepost=True para incluir dados mais recentes
        try:
            # Usa prepost=True para incluir dados pré-mercado e pós-mercado quando disponíveis
            hist = fii.history(period=periodo, timeout=15, prepost=False)
            
            # Se o período for curto (5d, 1mo), tenta buscar dados de hoje também
            if periodo in ['5d', '1mo', '3mo'] and not hist.empty:
                # Verifica se o último registro é de hoje
                from datetime import date
                hoje = date.today()
                ultima_data = hist.index[-1].date() if hasattr(hist.index[-1], 'date') else hist.index[-1].to_pydatetime().date()
                
                # Se não tem dados de hoje e o mercado pode estar aberto, tenta buscar intradiário
                if ultima_data < hoje:
                    print(f"  📅 Último registro é de {ultima_data}, tentando buscar dados de hoje...")
                    try:
                        hist_hoje = fii.history(period='1d', interval='1d', timeout=10)
                        if not hist_hoje.empty:
                            # Combina os dados
                            hist = hist.combine_first(hist_hoje)
                            print(f"  ✅ Dados de hoje adicionados!")
                    except Exception as e_hoje:
                        print(f"  ⚠️  Não conseguiu buscar dados de hoje: {str(e_hoje)}")
        except Exception as e:
            print(f"  ❌ Erro ao buscar histórico: {str(e)}")
            return jsonify({'erro': f'Timeout ao buscar dados de {ticker}. Tente novamente.'}), 500
        
        if hist.empty:
            print(f"  ❌ Nenhum dado disponível para {ticker} no período {periodo}")
            return jsonify({'erro': f'Nenhum dado disponível para {ticker} no período {periodo}'}), 404
        
        # Remove duplicatas se houver (mantém o último)
        hist = hist[~hist.index.duplicated(keep='last')]
        
        print(f"  ✅ {len(hist)} registros encontrados")
        print(f"  📅 Primeira data: {hist.index[0].strftime('%d/%m/%Y')}")
        print(f"  📅 Última data: {hist.index[-1].strftime('%d/%m/%Y')}")
        
        # Verifica se os dados são de hoje
        from datetime import date
        hoje = date.today()
        ultima_data = hist.index[-1].date()
        if ultima_data == hoje:
            print(f"  🟢 Dados atualizados (último registro é de HOJE)")
        else:
            diff = (hoje - ultima_data).days
            print(f"  🟡 Último registro é de {diff} dia(s) atrás ({ultima_data.strftime('%d/%m/%Y')})")
        
        # Calcula estatísticas
        preco_inicial = float(hist['Close'].iloc[0])
        preco_final = float(hist['Close'].iloc[-1])
        variacao_percentual = ((preco_final - preco_inicial) / preco_inicial) * 100
        
        response = {
            'ticker': ticker,
            'periodo': periodo,
            'intradiario': False,
            'dados': [
                {
                    'data': index.strftime('%Y-%m-%d'),
                    'abertura': float(row['Open']),
                    'fechamento': float(row['Close']),
                    'maxima': float(row['High']),
                    'minima': float(row['Low']),
                    'volume': int(row['Volume'])
                }
                for index, row in hist.iterrows()
            ],
            'estatisticas': {
                'preco_inicial': preco_inicial,
                'preco_final': preco_final,
                'preco_maximo': float(hist['High'].max()),
                'preco_minimo': float(hist['Low'].min()),
                'variacao_percentual': variacao_percentual,
                'volume_medio': float(hist['Volume'].mean()),
                'total_registros': len(hist)
            }
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"❌ Erro ao buscar cotações de {ticker}: {str(e)}")
        return jsonify({'erro': f'Erro ao buscar cotações: {str(e)}'}), 500

@app.route('/api/fii/<ticker>/analise-horarios', methods=['GET'])
def get_analise_horarios(ticker):
    """Analisa os melhores e piores horários para negociação nos últimos 30 dias"""
    try:
        # Adiciona .SA se não estiver presente
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        print(f"⏰ Analisando horários de negociação para {ticker} (últimos 30 dias)...")
        
        fii = yf.Ticker(ticker)
        
        # Busca dados intradiários dos últimos 30 dias
        # Yahoo Finance tem limitação: máximo 7 dias para intervalo de 5m
        # Para 30 dias, usamos intervalo de 1 hora
        try:
            hist = fii.history(period='1mo', interval='1h', timeout=20)
        except Exception as e:
            print(f"  ❌ Erro ao buscar dados horários: {str(e)}")
            return jsonify({'erro': f'Erro ao buscar dados horários: {str(e)}'}), 500
        
        if hist.empty:
            print(f"  ❌ Nenhum dado horário disponível para {ticker}")
            return jsonify({'erro': f'Nenhum dado horário disponível para {ticker}'}), 404
        
        print(f"  ✅ {len(hist)} registros horários encontrados")
        
        # Agrupa por hora do dia (0-23)
        import pandas as pd
        
        # Extrai hora e adiciona como coluna
        hist['hora_do_dia'] = hist.index.hour
        
        # Calcula estatísticas por hora
        estatisticas_por_hora = hist.groupby('hora_do_dia').agg({
            'Close': ['mean', 'min', 'max', 'count'],
            'Volume': 'mean'
        }).round(2)
        
        # Converte para dicionário com estrutura limpa
        analise_horarios = []
        for hora in range(24):
            if hora in estatisticas_por_hora.index:
                stats = estatisticas_por_hora.loc[hora]
                analise_horarios.append({
                    'hora': f"{hora:02d}:00",
                    'hora_num': hora,
                    'preco_medio': float(stats[('Close', 'mean')]),
                    'preco_minimo': float(stats[('Close', 'min')]),
                    'preco_maximo': float(stats[('Close', 'max')]),
                    'ocorrencias': int(stats[('Close', 'count')]),
                    'volume_medio': float(stats[('Volume', 'mean')])
                })
        
        # Ordena por preço médio para identificar melhores/piores horários
        analise_ordenada = sorted(analise_horarios, key=lambda x: x['preco_medio'])
        
        # Top 5 horários com menor preço médio (melhores para COMPRA)
        melhores_horarios_compra = analise_ordenada[:5]
        
        # Top 5 horários com maior preço médio (melhores para VENDA)
        melhores_horarios_venda = analise_ordenada[-5:][::-1]
        
        # Estatísticas gerais
        todos_precos = [h['preco_medio'] for h in analise_horarios]
        preco_medio_geral = sum(todos_precos) / len(todos_precos) if todos_precos else 0
        
        response = {
            'ticker': ticker,
            'periodo_analise': '30 dias',
            'total_horarios_analisados': len(analise_horarios),
            'total_registros': len(hist),
            'preco_medio_geral': round(preco_medio_geral, 2),
            'analise_completa': analise_horarios,
            'melhores_horarios_compra': melhores_horarios_compra,
            'melhores_horarios_venda': melhores_horarios_venda,
            'recomendacao': {
                'melhor_horario_compra': melhores_horarios_compra[0] if melhores_horarios_compra else None,
                'melhor_horario_venda': melhores_horarios_venda[0] if melhores_horarios_venda else None,
                'diferenca_percentual': round(
                    ((melhores_horarios_venda[0]['preco_medio'] - melhores_horarios_compra[0]['preco_medio']) / 
                     melhores_horarios_compra[0]['preco_medio'] * 100), 2
                ) if melhores_horarios_compra and melhores_horarios_venda else 0
            }
        }
        
        print(f"  📊 Melhor horário para COMPRA: {response['recomendacao']['melhor_horario_compra']['hora'] if response['recomendacao']['melhor_horario_compra'] else 'N/A'}")
        print(f"  📊 Melhor horário para VENDA: {response['recomendacao']['melhor_horario_venda']['hora'] if response['recomendacao']['melhor_horario_venda'] else 'N/A'}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Erro ao analisar horários de {ticker}: {str(e)}")
        return jsonify({'erro': f'Erro ao analisar horários: {str(e)}'}), 500

@app.route('/api/fii/<ticker>/dividendos', methods=['GET'])
def get_fii_dividendos(ticker):
    """Busca histórico de dividendos de um FII"""
    try:
        # Adiciona .SA se não estiver presente
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        # Se em modo demo, retorna dados mock
        if MODO_DEMO:
            print(f"⚠️  MODO DEMO: Retornando dividendos de exemplo para {ticker}")
            return jsonify(get_dividendos_mock(ticker))
        
        print(f"💰 Buscando dividendos de {ticker}...")
        
        fii = yf.Ticker(ticker)
        
        # Busca dividendos
        try:
            dividendos = fii.dividends
        except Exception as e:
            print(f"  ❌ Erro ao buscar dividendos: {str(e)}")
            return jsonify({'erro': f'Erro ao buscar dividendos de {ticker}'}), 500
        
        if dividendos is None or dividendos.empty:
            print(f"  ⚠️  Nenhum dividendo encontrado para {ticker}")
            # Retorna estrutura vazia mas válida
            return jsonify({
                'ticker': ticker,
                'dividendos': [],
                'dividend_yield': 0,
                'total_dividendos': 0,
                'mensagem': 'Nenhum dividendo encontrado ou dados não disponíveis'
            })
        
        print(f"  ✅ {len(dividendos)} dividendos encontrados")
        
        # Converte para lista de dicionários com formato correto para DividendosTab
        dividendos_list = [
            {
                'data_pagamento': index.strftime('%Y-%m-%d'),
                'data_com': index.strftime('%Y-%m-%d'),  # Usando mesma data (ideal seria ter data_com real)
                'valor': float(value),
                'tipo': 'Rendimento'
            }
            for index, value in dividendos.items()
        ]
        
        # Calcula estatísticas
        total_dividendos = float(dividendos.sum())
        media_dividendos = float(dividendos.mean())
        dividendo_maximo = float(dividendos.max())
        dividendo_minimo = float(dividendos.min())
        
        # Dividendos dos últimos 12 meses
        # Usa pd.Timestamp para garantir compatibilidade de timezone
        import pandas as pd
        data_limite = pd.Timestamp.now(tz=dividendos.index.tz) - pd.Timedelta(days=365)
        dividendos_12m = dividendos[dividendos.index >= data_limite]
        total_12m = float(dividendos_12m.sum()) if not dividendos_12m.empty else 0
        
        # Busca preço atual para calcular dividend yield
        preco_atual = 0
        try:
            info = fii.info
            preco_atual = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            # Se não conseguir do info, tenta do histórico
            if not preco_atual or preco_atual == 0:
                hist = fii.history(period='5d', timeout=10)
                if not hist.empty:
                    preco_atual = float(hist['Close'].iloc[-1])
        except Exception as e:
            print(f"  ⚠️  Não foi possível obter preço atual: {str(e)}")
            preco_atual = 0
        
        dividend_yield_12m = (total_12m / preco_atual) if preco_atual > 0 else 0
        
        response = {
            'ticker': ticker,
            'dividendos': dividendos_list,
            'dividend_yield': dividend_yield_12m,
            'estatisticas': {
                'total_dividendos': total_dividendos,
                'media_dividendos': media_dividendos,
                'dividendo_maximo': dividendo_maximo,
                'dividendo_minimo': dividendo_minimo,
                'total_registros': len(dividendos_list),
                'total_ultimos_12_meses': total_12m,
                'dividend_yield_12m': dividend_yield_12m,
                'preco_atual': preco_atual
            }
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"❌ Erro ao buscar dividendos de {ticker}: {str(e)}")
        return jsonify({'erro': f'Erro ao buscar dividendos: {str(e)}'}), 500

@app.route('/api/fii/<ticker>/resumo', methods=['GET'])
def get_fii_resumo(ticker):
    """Busca resumo completo de um FII (cotações + dividendos)"""
    try:
        # Adiciona .SA se não estiver presente
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"
        
        fii = yf.Ticker(ticker)
        info = fii.info
        
        # Histórico de preços
        hist_1y = fii.history(period='1y')
        hist_1mo = fii.history(period='1mo')
        hist_1d = fii.history(period='1d')
        
        # Dividendos
        dividendos = fii.dividends
        data_limite = datetime.now() - timedelta(days=365)
        dividendos_12m = dividendos[dividendos.index >= data_limite] if not dividendos.empty else []
        
        # Preço atual
        preco_atual = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        response = {
            'ticker': ticker,
            'nome': info.get('longName', ticker),
            'preco_atual': preco_atual,
            'cotacoes': {
                'diaria': {
                    'variacao': info.get('regularMarketChangePercent', 0),
                    'abertura': float(hist_1d['Open'].iloc[0]) if not hist_1d.empty else 0,
                    'maxima': float(hist_1d['High'].max()) if not hist_1d.empty else 0,
                    'minima': float(hist_1d['Low'].min()) if not hist_1d.empty else 0,
                    'volume': int(hist_1d['Volume'].iloc[0]) if not hist_1d.empty else 0
                },
                'mensal': {
                    'variacao': ((float(hist_1mo['Close'].iloc[-1]) - float(hist_1mo['Close'].iloc[0])) / float(hist_1mo['Close'].iloc[0]) * 100) if not hist_1mo.empty and len(hist_1mo) > 1 else 0,
                    'maxima': float(hist_1mo['High'].max()) if not hist_1mo.empty else 0,
                    'minima': float(hist_1mo['Low'].min()) if not hist_1mo.empty else 0,
                    'volume_medio': float(hist_1mo['Volume'].mean()) if not hist_1mo.empty else 0
                },
                'anual': {
                    'variacao': ((float(hist_1y['Close'].iloc[-1]) - float(hist_1y['Close'].iloc[0])) / float(hist_1y['Close'].iloc[0]) * 100) if not hist_1y.empty and len(hist_1y) > 1 else 0,
                    'maxima': float(hist_1y['High'].max()) if not hist_1y.empty else 0,
                    'minima': float(hist_1y['Low'].min()) if not hist_1y.empty else 0,
                    'maxima_52_semanas': info.get('fiftyTwoWeekHigh', 0),
                    'minima_52_semanas': info.get('fiftyTwoWeekLow', 0)
                }
            },
            'dividendos': {
                'total_12_meses': float(dividendos_12m.sum()) if len(dividendos_12m) > 0 else 0,
                'quantidade_12_meses': len(dividendos_12m) if len(dividendos_12m) > 0 else 0,
                'media_mensal': float(dividendos_12m.mean()) if len(dividendos_12m) > 0 else 0,
                'dividend_yield': info.get('dividendYield', 0),
                'ultimo_dividendo': float(dividendos.iloc[-1]) if not dividendos.empty else 0,
                'data_ultimo_dividendo': dividendos.index[-1].strftime('%Y-%m-%d') if not dividendos.empty else None
            }
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/analise-ia', methods=['POST'])
def gerar_analise_ia():
    """Gera análise de IA para oportunidades de FIIs"""
    try:
        if not client:
            return jsonify({'erro': 'OpenAI API não configurada'}), 500
        
        data = request.json
        maiores_altas = data.get('maioresAltas', [])
        maiores_baixas = data.get('maioresBaixas', [])
        maiores_descontos = data.get('maioresDescontos', [])
        estatisticas = data.get('estatisticas', {})
        
        print("🤖 Gerando análise de IA para FIIs...")
        
        # 🔍 NOVA FUNCIONALIDADE: Pesquisa informações web sobre os FIIs principais
        print("🌐 Pesquisando informações na web sobre os FIIs...")
        
        # Coleta tickers principais (top 3 altas + top 3 baixas + descontos)
        tickers_pesquisa = []
        for fii in (maiores_altas[:3] + maiores_baixas[:3] + maiores_descontos[:2]):
            ticker = fii['ticker'].replace('.SA', '')
            if ticker not in tickers_pesquisa:
                tickers_pesquisa.append(ticker)
        
        # Realiza pesquisa web
        informacoes_web = {}
        if tickers_pesquisa:
            try:
                informacoes_web = pesquisar_multiplos_fiis(tickers_pesquisa)
                print(f"  ✅ Pesquisa concluída para {len(informacoes_web)} FIIs")
            except Exception as e:
                print(f"  ⚠️  Erro na pesquisa web: {str(e)}")
                informacoes_web = {}
        
        # Monta contexto enriquecido com informações setoriais
        # NOTA: dividend_yield do Yahoo já vem em percentual (12.45 = 12.45%)
        def formatar_fii_contexto(fii):
            setor_info = get_setor_info(fii['ticker'])
            return (f"- {fii['ticker']} ({setor_info['setor']} - {setor_info['tipo']}): "
                   f"Preço R$ {fii['preco']:.2f}, Variação {fii['variacao']:+.2f}%, "
                   f"P/VP {fii.get('pvp', 'N/A')}, DY {fii.get('dy', 0):.2f}%")
        
        contexto_altas = "\n".join([formatar_fii_contexto(fii) for fii in maiores_altas])
        contexto_baixas = "\n".join([formatar_fii_contexto(fii) for fii in maiores_baixas])
        
        # Separa descontos: em BAIXA (oportunidade tática) vs em ALTA/ESTÁVEL
        contexto_descontos = ""
        descontos_em_baixa = []
        descontos_outros = []
        
        if maiores_descontos and len(maiores_descontos) > 0:
            for fii in maiores_descontos:
                if fii.get('emBaixa', False):
                    descontos_em_baixa.append(fii)
                else:
                    descontos_outros.append(fii)
            
            if descontos_em_baixa:
                contexto_descontos += "\n🔥 DESCONTOS AUMENTANDO (Em Baixa Hoje - Oportunidade Tática):\n"
                contexto_descontos += "\n".join([
                    f"- {fii['ticker']} ({get_setor_info(fii['ticker'])['setor']}): "
                    f"P/VP {fii.get('pvp', 0):.2f} (Desconto {fii.get('desconto', 0):.1f}%), "
                    f"Variação {fii.get('variacao', 0):+.2f}%, "
                    f"DY {fii.get('dy', 0):.2f}%"
                    for fii in descontos_em_baixa
                ])
            
            if descontos_outros:
                contexto_descontos += "\n\n💎 Outros Descontos (Estáveis ou em Alta):\n"
                contexto_descontos += "\n".join([
                    f"- {fii['ticker']} ({get_setor_info(fii['ticker'])['setor']}): "
                    f"P/VP {fii.get('pvp', 0):.2f} (Desconto {fii.get('desconto', 0):.1f}%), "
                    f"DY {fii.get('dy', 0):.2f}%"
                    for fii in descontos_outros
                ])
        
        # Análise setorial detalhada
        from collections import Counter
        
        # Conta setores nas altas e baixas
        setores_altas = [get_setor_info(fii['ticker'])['setor'] for fii in maiores_altas]
        setores_baixas = [get_setor_info(fii['ticker'])['setor'] for fii in maiores_baixas]
        
        contagem_altas = Counter(setores_altas)
        contagem_baixas = Counter(setores_baixas)
        
        # Monta resumo estatístico por setor
        setores_unicos = list(set(setores_altas + setores_baixas))
        
        resumo_setorial = "DISTRIBUIÇÃO SETORIAL:\n"
        resumo_setorial += "─────────────────────\n"
        for setor in setores_unicos:
            altas = contagem_altas.get(setor, 0)
            baixas = contagem_baixas.get(setor, 0)
            resumo_setorial += f"• {setor}: {altas} em alta, {baixas} em baixa\n"
        
        # Características detalhadas dos setores
        info_setorial = "\n\n".join([
            f"**{setor}**:\n" + 
            f"• Valoriza com: {', '.join(CARACTERISTICAS_SETORES.get(setor, {}).get('valoriza_com', [])[:3])}\n" +
            f"• Desvaloriza com: {', '.join(CARACTERISTICAS_SETORES.get(setor, {}).get('desvaloriza_com', [])[:3])}\n" +
            f"• Índices correlacionados: {', '.join(CARACTERISTICAS_SETORES.get(setor, {}).get('indices_correlacionados', []))}"
            for setor in setores_unicos if setor in CARACTERISTICAS_SETORES
        ])
        
        # Monta contexto adicional da pesquisa web
        contexto_web = ""
        if informacoes_web:
            contexto_web = "\n═══════════════════════════════════════════════\n"
            contexto_web += "INFORMAÇÕES ADICIONAIS DA WEB:\n"
            contexto_web += "═══════════════════════════════════════════════\n"
            
            for ticker, info in informacoes_web.items():
                if info.get('fontes_consultadas'):
                    contexto_web += f"\n**{ticker}**:\n"
                    contexto_web += f"Fontes: {', '.join(info['fontes_consultadas'])}\n"
                    
                    if info.get('resumo_geral'):
                        contexto_web += f"• {info['resumo_geral'][:200]}...\n"
                    
                    if info.get('dados_setor'):
                        contexto_web += f"• {info['dados_setor']}\n"
                    
                    if info.get('noticias_recentes'):
                        contexto_web += f"• Notícias: {info['noticias_recentes'][0][:100]}...\n"
        
        # Prompt focado em análise de mercado e movimentos setoriais
        prompt = f"""Você é um analista EXPERIENTE de FIIs focado em interpretar movimentos de mercado.

OBJETIVO: Analisar os dados e explicar O QUE ESTÁ ACONTECENDO no mercado de FIIs HOJE.

REGRAS:
⛔ Use APENAS os dados fornecidos - NUNCA invente informações
⛔ Foque em INTERPRETAR os movimentos, não em recomendar fundos específicos
⛔ Analise PADRÕES SETORIAIS e tendências macro
⛔ Se citar fonte web, use EXATAMENTE o nome da fonte

═══════════════════════════════════════════════
DADOS DO MERCADO HOJE:
═══════════════════════════════════════════════
• Total analisados: {estatisticas.get('total', 0)} FIIs
• Em ALTA: {estatisticas.get('emAlta', 0)} ({(estatisticas.get('emAlta', 0) / max(estatisticas.get('total', 1), 1) * 100):.1f}%)
• Em BAIXA: {estatisticas.get('emBaixa', 0)} ({(estatisticas.get('emBaixa', 0) / max(estatisticas.get('total', 1), 1) * 100):.1f}%)
• Variação média: {estatisticas.get('variacaoMedia', 0):+.2f}%

{resumo_setorial}

═══════════════════════════════════════════════
TOP 5 MAIORES ALTAS DO DIA:
═══════════════════════════════════════════════
{contexto_altas}

═══════════════════════════════════════════════
TOP 5 MAIORES BAIXAS DO DIA:
═══════════════════════════════════════════════
{contexto_baixas}
{'═══════════════════════════════════════════════' if contexto_descontos else ''}
{'DESCONTOS P/VP (Abaixo do Valor Patrimonial):' if contexto_descontos else ''}
{'═══════════════════════════════════════════════' if contexto_descontos else ''}
{contexto_descontos}
{'⚠️  ATENÇÃO: ' + str(len(descontos_em_baixa)) + ' fundos com DESCONTO AUMENTANDO (em baixa hoje)!' if descontos_em_baixa else ''}

═══════════════════════════════════════════════
CARACTERÍSTICAS SETORIAIS (FATORES MACRO):
═══════════════════════════════════════════════
{info_setorial}
{contexto_web}

═══════════════════════════════════════════════
SUA MISSÃO - ANÁLISE EM 4 PARÁGRAFOS:
═══════════════════════════════════════════════

**PARÁGRAFO 1 - LEITURA DO DIA (2-3 frases):**
Interprete o movimento geral: mercado em alta, baixa ou neutro? 
Qual % de fundos em alta vs baixa? O que isso indica sobre o sentimento?
Exemplo: "Mercado misto com 60% em alta. Concentração de ganhos em [SETOR], enquanto [SETOR] recua."

**PARÁGRAFO 2 - ANÁLISE SETORIAL DAS ALTAS (3-4 frases):**
Olhe os 5 maiores altas e identifique:
- Quais SETORES dominam? (ex: 3 de Recebíveis, 2 de Logística)
- POR QUE esses setores sobem hoje? Use "CARACTERÍSTICAS SETORIAIS"
- Há coerência macro? (ex: Selic alta favorece Recebíveis)
Cite TODOS os setores em alta, não só 1 ou 2!
Exemplo: "Altas lideradas por Recebíveis (MXRF11, VRTA11, MCRE11) que se beneficiam da Selic elevada. Logística (XPLG11) também sobe com e-commerce forte."

**PARÁGRAFO 3 - ANÁLISE SETORIAL DAS BAIXAS (3-4 frases):**
Olhe os 5 maiores baixas e identifique:
- Quais SETORES estão em queda?
- POR QUE esses setores caem? Use "CARACTERÍSTICAS SETORIAIS"
- Há risco macro? (ex: Shoppings sensíveis à recessão)
Cite TODOS os setores em baixa!
Exemplo: "Baixas concentradas em Lajes Corporativas (OUJP11, RBRP11) por temor de vacância com home office. Shoppings (HSML11) também recuam com consumo fraco."

**PARÁGRAFO 4 - SÍNTESE E OPORTUNIDADES TÁTICAS (3-4 frases):**
Resuma a tese do dia e destaque oportunidades:
- Rotação setorial ou movimento amplo?
- Se houver "DESCONTOS AUMENTANDO": mencione especificamente! São fundos em baixa + P/VP < 1 = possível entrada tática
- Explique POR QUE esses descontos estão aumentando (use setor + baixa do dia)
- Próximos catalisadores a observar
Exemplo: "HGRU11 aparece com desconto aumentando (P/VP 0.92, -1.5%) - setor de Desenvolvimento sofre com Selic alta. Pode ser entrada tática para quem acredita em queda de juros. Atenção aos dados de inflação."

═══════════════════════════════════════════════
REGRAS FINAIS:
═══════════════════════════════════════════════
✅ Analise TODOS os 5 fundos em alta e TODOS os 5 em baixa - não foque só em 1 ou 2
✅ Identifique PADRÕES SETORIAIS (não fundos isolados)
✅ Relacione movimentos com "CARACTERÍSTICAS SETORIAIS" (Selic, consumo, etc)
✅ Use setores EXATOS mostrados nos dados
✅ Se houver "DESCONTOS AUMENTANDO", SEMPRE mencione no parágrafo 4 com ticker, P/VP e motivo
✅ Se houver info web, cite fonte: "Segundo [FONTE]..."
✅ Máximo 400 palavras (aumentado para incluir análise de descontos)
✅ Tom: Analítico, objetivo, educativo

Sua análise:"""

        # Chama API da OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """Você é um analista de mercado de FIIs especializado em interpretar movimentos setoriais.

SUA MISSÃO:
- Identificar PADRÕES e TENDÊNCIAS nos dados
- Explicar POR QUE os setores sobem ou caem (use características setoriais)
- Analisar TODOS os fundos mostrados, não apenas alguns
- Conectar movimentos a fatores macro (Selic, PIB, consumo)

NUNCA FAÇA:
- Inventar informações não fornecidas
- Focar em apenas 1 ou 2 fundos específicos
- Recomendar compras sem analisar o contexto setorial
- Especular sobre gestoras ou ativos sem dados

SEMPRE FAÇA:
- Analise os 5 fundos em alta E os 5 em baixa
- Identifique quais setores dominam cada grupo
- Explique causas usando "Características Setoriais"
- Se houver "DESCONTOS AUMENTANDO", mencione no parágrafo 4 com ticker, P/VP e contexto
- Seja analítico, educativo e baseado em dados"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,  # Um pouco mais criativo para análise contextual
            max_tokens=650  # Mais espaço para análise completa com descontos
        )
        
        analise = response.choices[0].message.content
        
        print(f"  ✅ Análise gerada com sucesso!")
        
        return jsonify({
            'analise': analise,
            'timestamp': datetime.now().isoformat(),
            'modelo': 'gpt-4o-mini'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar análise de IA: {str(e)}")
        return jsonify({'erro': f'Erro ao gerar análise: {str(e)}'}), 500

if __name__ == '__main__':
    # Permite porta dinâmica via variável de ambiente
    port = int(os.getenv('FLASK_RUN_PORT', 5001))
    app.run(debug=True, port=port, host='127.0.0.1')

