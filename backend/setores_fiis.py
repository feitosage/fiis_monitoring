"""
Mapeamento de FIIs por Setor e Características
"""

# Classificação setorial dos FIIs
SETORES_FIIS = {
    # Logística e Galpões
    'HGLG11': {'setor': 'Logística', 'tipo': 'Galpões Logísticos'},
    'XPLG11': {'setor': 'Logística', 'tipo': 'Galpões Logísticos'},
    
    # Shoppings
    'VISC11': {'setor': 'Shopping Centers', 'tipo': 'Varejo'},
    'HSML11': {'setor': 'Shopping Centers', 'tipo': 'Varejo'},
    'VILG11': {'setor': 'Shopping Centers', 'tipo': 'Varejo (High-end)'},
    'XPML11': {'setor': 'Shopping Centers', 'tipo': 'Varejo'},
    
    # Lajes Corporativas
    'OUJP11': {'setor': 'Lajes Corporativas', 'tipo': 'Escritórios'},
    'LVBI11': {'setor': 'Lajes Corporativas', 'tipo': 'Escritórios'},
    'RBRP11': {'setor': 'Lajes Corporativas', 'tipo': 'Escritórios AAA'},
    
    # Recebíveis / Papel
    'MXRF11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'CRI/CRA'},
    'VRTA11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'CRI'},
    'MCRE11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'CRI/CRA'},
    'CPTS11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'CRI/CRA'},
    'KNRI11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'Renda Fixa Imobiliária'},
    'KNCR11': {'setor': 'Recebíveis Imobiliários', 'tipo': 'CRI'},
    
    # Desenvolvimento / Tijolo
    'TRXF11': {'setor': 'Desenvolvimento', 'tipo': 'Renda Urbana'},
    'HGRU11': {'setor': 'Desenvolvimento', 'tipo': 'Renda Urbana'},
    'RZTR11': {'setor': 'Terrenos', 'tipo': 'Desenvolvimento Urbano'},
    
    # Fundos de Fundos / Híbridos
    'VGHF11': {'setor': 'Fundos de Fundos', 'tipo': 'Multi-estratégia'},
    
    # Agroindustrial
    'RURA11': {'setor': 'Agronegócio', 'tipo': 'FIAGRO'},
    
    # Outros
    'PVBI11': {'setor': 'Híbrido', 'tipo': 'Multi-ativos'},
    'BTLG11': {'setor': 'Logística', 'tipo': 'Galpões'},
}

# Características de valorização por setor
CARACTERISTICAS_SETORES = {
    'Logística': {
        'valoriza_com': [
            'Crescimento do e-commerce',
            'Expansão da economia',
            'Aumento das exportações',
            'Redução da taxa Selic'
        ],
        'desvaloriza_com': [
            'Recessão econômica',
            'Alta da taxa Selic',
            'Redução do consumo',
            'Concorrência de novos galpões'
        ],
        'indices_correlacionados': ['PIB', 'PMI Industrial', 'Selic (inverso)'],
        'resiliente': True,
        'descricao': 'Demanda estrutural do e-commerce e exportações'
    },
    
    'Shopping Centers': {
        'valoriza_com': [
            'Aumento do consumo',
            'Renda da população crescendo',
            'Redução do desemprego',
            'Festividades e datas comemorativas'
        ],
        'desvaloriza_com': [
            'Recessão e desemprego',
            'Concorrência do e-commerce',
            'Alta da Selic (reduz consumo)',
            'Vacância de lojas'
        ],
        'indices_correlacionados': ['PMC (Vendas Varejo)', 'Desemprego (inverso)', 'Selic (inverso)'],
        'resiliente': False,
        'descricao': 'Sensível ao ciclo econômico e consumo'
    },
    
    'Lajes Corporativas': {
        'valoriza_com': [
            'Retorno ao trabalho presencial',
            'Crescimento de empresas',
            'Inflação de aluguéis (IPCA)',
            'Localização premium'
        ],
        'desvaloriza_com': [
            'Home office permanente',
            'Recessão empresarial',
            'Alta vacância',
            'Regiões desvalorizadas'
        ],
        'indices_correlacionados': ['IPCA', 'PIB Serviços', 'IGP-M'],
        'resiliente': False,
        'descricao': 'Risco de vacância por mudança de modelo de trabalho'
    },
    
    'Recebíveis Imobiliários': {
        'valoriza_com': [
            'Alta da taxa Selic',
            'CDI elevado',
            'Spread de crédito atrativo',
            'Indexação a índices (IPCA+)'
        ],
        'desvaloriza_com': [
            'Queda da Selic',
            'CDI baixo',
            'Inadimplência de devedores',
            'Risco de crédito'
        ],
        'indices_correlacionados': ['Selic', 'CDI', 'IPCA', 'TR'],
        'resiliente': True,
        'descricao': 'Proteção contra inflação e juros altos'
    },
    
    'Desenvolvimento': {
        'valoriza_com': [
            'Valorização imobiliária',
            'Crescimento urbano',
            'Demanda por imóveis',
            'Redução de juros'
        ],
        'desvaloriza_com': [
            'Alta da Selic',
            'Crise imobiliária',
            'Excesso de oferta',
            'Risco de execução de projetos'
        ],
        'indices_correlacionados': ['Selic (inverso)', 'PIB Construção', 'IGMI-R'],
        'resiliente': False,
        'descricao': 'Alto risco por depender de execução de projetos'
    },
    
    'Terrenos': {
        'valoriza_com': [
            'Expansão urbana',
            'Valorização de terrenos',
            'Demanda por desenvolvimento',
            'Infraestrutura na região'
        ],
        'desvaloriza_com': [
            'Alta da Selic',
            'Crise na construção civil',
            'Falta de demanda',
            'Localização ruim'
        ],
        'indices_correlacionados': ['Selic (inverso)', 'IGMI-R', 'PIB Construção'],
        'resiliente': False,
        'descricao': 'Volatilidade alta e dependência de ciclo imobiliário'
    },
    
    'Fundos de Fundos': {
        'valoriza_com': [
            'Diversificação de setores',
            'Gestão ativa competente',
            'Diferentes indexadores'
        ],
        'desvaloriza_com': [
            'Taxa de administração elevada',
            'Performance ruim dos fundos investidos',
            'Complexidade excessiva'
        ],
        'indices_correlacionados': ['Mix de índices'],
        'resiliente': True,
        'descricao': 'Diversificação natural mas com taxa de gestão dupla'
    },
    
    'Agronegócio': {
        'valoriza_com': [
            'Preços de commodities',
            'Exportações agrícolas',
            'Safra recorde',
            'Dólar alto'
        ],
        'desvaloriza_com': [
            'Quebra de safra',
            'Queda de commodities',
            'Dólar baixo',
            'Clima adverso'
        ],
        'indices_correlacionados': ['Commodities', 'Dólar', 'Safra'],
        'resiliente': False,
        'descricao': 'Alto risco climático e volatilidade de commodities'
    },
    
    'Híbrido': {
        'valoriza_com': [
            'Diversificação de ativos',
            'Gestão ativa',
            'Mix de indexadores'
        ],
        'desvaloriza_com': [
            'Falta de especialização',
            'Gestão inconsistente'
        ],
        'indices_correlacionados': ['Mix variado'],
        'resiliente': True,
        'descricao': 'Diversificado mas sem especialização clara'
    }
}

def get_setor_info(ticker):
    """Retorna informações do setor de um FII"""
    ticker_clean = ticker.replace('.SA', '')
    info = SETORES_FIIS.get(ticker_clean, {
        'setor': 'Desconhecido',
        'tipo': 'N/A'
    })
    
    setor = info['setor']
    caracteristicas = CARACTERISTICAS_SETORES.get(setor, {
        'valoriza_com': [],
        'desvaloriza_com': [],
        'indices_correlacionados': [],
        'resiliente': False,
        'descricao': 'Informações não disponíveis'
    })
    
    return {
        **info,
        **caracteristicas
    }

