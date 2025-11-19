# Dados mock para testar quando Yahoo Finance está indisponível

FIIS_MOCK = [
    {
        'ticker': 'HGLG11.SA',
        'nome': 'CSHG Logística FII',
        'preco_atual': 153.50,
        'variacao_dia': 0.0195,
        'dividend_yield': 0.0856,
        'volume': 1523400
    },
    {
        'ticker': 'KNRI11.SA',
        'nome': 'Kinea Renda Imobiliária FII',
        'preco_atual': 98.75,
        'variacao_dia': -0.0051,
        'dividend_yield': 0.0923,
        'volume': 2145800
    },
    {
        'ticker': 'VISC11.SA',
        'nome': 'Vinci Shopping Centers FII',
        'preco_atual': 87.30,
        'variacao_dia': 0.0123,
        'dividend_yield': 0.0789,
        'volume': 987600
    },
    {
        'ticker': 'MXRF11.SA',
        'nome': 'Maxi Renda FII',
        'preco_atual': 9.85,
        'variacao_dia': 0.0076,
        'dividend_yield': 0.1045,
        'volume': 3421500
    },
    {
        'ticker': 'BTLG11.SA',
        'nome': 'BTG Pactual Logística FII',
        'preco_atual': 102.45,
        'variacao_dia': -0.0034,
        'dividend_yield': 0.0812,
        'volume': 1876300
    },
]

def get_fii_mock_details(ticker):
    """Retorna detalhes mock de um FII"""
    fii_data = {
        'HGLG11.SA': {
            'ticker': 'HGLG11.SA',
            'nome': 'CSHG Logística FII',
            'preco_atual': 153.50,
            'variacao_dia': 0.0195,
            'dividend_yield': 0.0856,
            'volume': 1523400,
            'minima_52_semanas': 142.30,
            'maxima_52_semanas': 167.80,
            'historico': [
                {'data': '2025-09-22', 'fechamento': 151.20, 'volume': 1234500},
                {'data': '2025-09-23', 'fechamento': 152.10, 'volume': 987600},
                {'data': '2025-09-24', 'fechamento': 153.50, 'volume': 1523400},
                {'data': '2025-10-01', 'fechamento': 152.80, 'volume': 1345200},
                {'data': '2025-10-02', 'fechamento': 153.50, 'volume': 1523400},
            ]
        }
    }
    
    return fii_data.get(ticker, fii_data['HGLG11.SA'])

def get_dividendos_mock(ticker):
    """Retorna dividendos mock"""
    return {
        'ticker': ticker,
        'dividendos': [
            {'data': '2025-01-15', 'valor': 1.25},
            {'data': '2025-02-15', 'valor': 1.18},
            {'data': '2025-03-15', 'valor': 1.32},
            {'data': '2025-04-15', 'valor': 1.28},
            {'data': '2025-05-15', 'valor': 1.35},
            {'data': '2025-06-15', 'valor': 1.22},
            {'data': '2025-07-15', 'valor': 1.30},
            {'data': '2025-08-15', 'valor': 1.27},
            {'data': '2025-09-15', 'valor': 1.33},
            {'data': '2025-10-15', 'valor': 1.29},
        ],
        'estatisticas': {
            'total_dividendos': 12.79,
            'media_dividendos': 1.28,
            'dividendo_maximo': 1.35,
            'dividendo_minimo': 1.18,
            'total_registros': 10,
            'total_ultimos_12_meses': 15.36,
            'dividend_yield_12m': 0.1001,
            'preco_atual': 153.50
        }
    }

