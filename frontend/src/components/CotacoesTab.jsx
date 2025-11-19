import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, ReferenceLine } from 'recharts'
import { TrendingUp, TrendingDown, BarChart3, Activity, DollarSign, Calendar, RefreshCw } from 'lucide-react'
import {
  calculatePriceDomain,
  formatCurrency,
  formatNumber,
  formatPercent,
  formatDate,
  processHistoricalData,
  calculateStats,
  CHART_COLORS,
  defaultTooltipStyle,
  defaultGridStyle,
  defaultAxisStyle
} from '../utils/chartUtils'
import './CotacoesTab.css'

function CotacoesTab({ ticker }) {
  const [periodo, setPeriodo] = useState('1y')
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [chartType, setChartType] = useState('area') // 'area' ou 'line'
  const [apiVersion, setApiVersion] = useState(Date.now()) // Força bypass de cache
  const [analiseHorarios, setAnaliseHorarios] = useState(null) // Análise de horários
  const [loadingHorarios, setLoadingHorarios] = useState(false) // Loading análise de horários

  useEffect(() => {
    if (ticker) {
      buscarCotacoes()
      buscarAnaliseHorarios()
    }
  }, [ticker, periodo])

  const buscarCotacoes = async () => {
    setLoading(true)
    setError(null)

    try {
      // Força bypass TOTAL de cache com múltiplos parâmetros
      const timestamp = Date.now()
      const random = Math.random().toString(36).substring(7)
      const response = await fetch(
        `http://localhost:5001/api/fii/${ticker}/cotacoes?periodo=${periodo}&_t=${timestamp}&_v=${apiVersion}&_r=${random}`,
        {
          cache: 'no-store', // Mais agressivo que 'no-cache'
          headers: {
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        }
      )

      if (!response.ok) {
        throw new Error('Erro ao buscar cotações')
      }

      const data = await response.json()
      
      // Log SUPER DETALHADO para debug
      console.log('═══════════════════════════════════════════════════════')
      console.log(`📊 DADOS RECEBIDOS para ${ticker} (${periodo})`)
      console.log('═══════════════════════════════════════════════════════')
      console.log('Total de registros:', data.estatisticas.total_registros)
      console.log('Primeira data:', data.dados[0]?.data)
      console.log('Última data:', data.dados[data.dados.length - 1]?.data)
      console.log('Intradiário?', data.intradiario)
      console.log('\n📅 ÚLTIMAS 5 DATAS:')
      data.dados.slice(-5).forEach((d, i) => {
        console.log(`  ${i+1}. ${d.data} - Fechamento: R$ ${d.fechamento?.toFixed(2)}`)
      })
      console.log('═══════════════════════════════════════════════════════')
      console.log('🔥 Se você vê 21/10 na tela mas aqui mostra 22/10 = CACHE!')
      console.log('💡 Solução: Ctrl+Shift+R ou Modo Anônimo')
      console.log('═══════════════════════════════════════════════════════\n')
      
      setDados(data)
    } catch (err) {
      setError(err.message)
      console.error('Erro:', err)
    } finally {
      setLoading(false)
    }
  }

  const buscarAnaliseHorarios = async () => {
    setLoadingHorarios(true)
    
    try {
      const timestamp = Date.now()
      const response = await fetch(
        `http://localhost:5001/api/fii/${ticker}/analise-horarios?_t=${timestamp}`,
        {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-store, no-cache, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        }
      )

      if (!response.ok) {
        throw new Error('Erro ao buscar análise de horários')
      }

      const data = await response.json()
      setAnaliseHorarios(data)
      console.log('📊 Análise de horários:', data)
    } catch (err) {
      console.error('Erro ao buscar análise de horários:', err)
      setAnaliseHorarios(null)
    } finally {
      setLoadingHorarios(false)
    }
  }

  const getVariationClass = (value) => {
    if (value > 0) return 'positive'
    if (value < 0) return 'negative'
    return 'neutral'
  }

  const periodos = [
    { value: '1d', label: '1D', icon: '📅' },
    { value: '5d', label: '5D', icon: '📅' },
    { value: '1mo', label: '1M', icon: '📆' },
    { value: '3mo', label: '3M', icon: '📆' },
    { value: '6mo', label: '6M', icon: '📆' },
    { value: '1y', label: '1A', icon: '🗓️' },
    { value: '2y', label: '2A', icon: '🗓️' },
    { value: '5y', label: '5A', icon: '🗓️' },
    { value: 'max', label: 'Máx', icon: '🗓️' }
  ]

  if (!ticker) {
    return (
      <div className="cotacoes-tab">
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>Selecione um FII</h3>
          <p>Escolha um fundo para visualizar as cotações históricas</p>
        </div>
      </div>
    )
  }

  // Processa dados - intradiários ou diários
  const chartData = dados ? (dados.intradiario ? 
    // Dados intradiários com hora
    dados.dados.map(item => ({
      date: item.timestamp,
      value: item.fechamento,
      dateFormatted: item.hora // Mostra apenas hora (HH:MM)
    })) :
    // Dados diários normais
    processHistoricalData(dados.dados, 'fechamento')
  ) : []
  
  const domain = calculatePriceDomain(chartData)
  const stats = calculateStats(chartData)
  
  // Calcula média móvel simples (apenas para dados diários)
  const calcularMediaMovel = (data, periodos = 20) => {
    // Não calcula MM para dados intradiários
    if (dados?.intradiario) {
      return data
    }
    
    return data.map((item, index) => {
      if (index < periodos - 1) return { ...item, media: null }
      
      const slice = data.slice(index - periodos + 1, index + 1)
      const sum = slice.reduce((acc, d) => acc + d.value, 0)
      const media = sum / periodos
      
      return { ...item, media }
    })
  }

  const chartDataWithMA = chartData.length > 0 ? calcularMediaMovel(chartData, 20) : []
  const isIntraday = dados?.intradiario || false
  
  // Verifica se os dados são de hoje (FIX: corrigido timezone)
  const isDadosHoje = () => {
    if (!dados || !dados.dados || dados.dados.length === 0) return false
    
    // Extrai apenas a data sem conversão de timezone
    const ultimaDataStr = dados.dados[dados.dados.length - 1].data
    const [ano, mes, dia] = ultimaDataStr.split('T')[0].split('-')
    const ultimaData = `${ano}-${mes}-${dia}`
    
    const hoje = new Date()
    const hojeStr = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`
    
    return ultimaData === hojeStr
  }
  
  // Verifica se os dados estão MUITO desatualizados (mais de 2 dias) (FIX: corrigido timezone)
  const isDadosMuitoAntigos = () => {
    if (!dados || !dados.dados || dados.dados.length === 0) return false
    
    // Extrai apenas a data sem conversão de timezone
    const ultimaDataStr = dados.dados[dados.dados.length - 1].data
    const [ano, mes, dia] = ultimaDataStr.split('T')[0].split('-')
    
    const ultimaData = new Date(parseInt(ano), parseInt(mes) - 1, parseInt(dia))
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0) // Reseta hora para comparar apenas datas
    ultimaData.setHours(0, 0, 0, 0)
    
    const diffDias = Math.floor((hoje - ultimaData) / (1000 * 60 * 60 * 24))
    return diffDias > 2
  }
  
  const dadosAtualizados = isDadosHoje()
  const dadosMuitoAntigos = isDadosMuitoAntigos()

  return (
    <div className="cotacoes-tab">
      <div className="cotacoes-header">
        <div className="header-title-section">
          <h3 className="cotacoes-title">
            <BarChart3 size={28} />
            Cotações Históricas
          </h3>
          <span className="ticker-badge">{ticker.replace('.SA', '')}</span>
          {dados && !loading && (
            <>
              <span 
                className={`status-badge ${dadosAtualizados ? 'atualizado' : 'desatualizado'}`}
                title={dadosAtualizados ? 'Dados atualizados de hoje' : 'Dados do último dia útil'}
              >
                {dadosAtualizados ? '🟢 Atualizado' : '🟡 Último dia útil'}
              </span>
              <button
                className="refresh-button"
                onClick={() => {
                  setApiVersion(Date.now()) // Força nova versão da API
                  buscarCotacoes()
                }}
                disabled={loading}
                title="Atualizar dados (força busca sem cache)"
              >
                <RefreshCw size={18} className={loading ? 'spinning' : ''} />
                Atualizar
              </button>
            </>
          )}
        </div>
        
        <div className="controls-section">
          {/* Tipo de Gráfico */}
          <div className="chart-type-selector">
            <button
              className={`chart-type-btn ${chartType === 'area' ? 'active' : ''}`}
              onClick={() => setChartType('area')}
              title="Gráfico de Área"
            >
              <Activity size={16} />
              Área
            </button>
            <button
              className={`chart-type-btn ${chartType === 'line' ? 'active' : ''}`}
              onClick={() => setChartType('line')}
              title="Gráfico de Linha"
            >
              <TrendingUp size={16} />
              Linha
            </button>
          </div>

          {/* Seletor de Período */}
          <div className="periodo-selector">
            {periodos.map((p) => (
              <button
                key={p.value}
                className={`periodo-button ${periodo === p.value ? 'active' : ''}`}
                onClick={() => setPeriodo(p.value)}
                disabled={loading}
                title={p.label}
              >
                <span className="periodo-icon">{p.icon}</span>
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando cotações...</p>
        </div>
      )}
      
      {error && (
        <div className="error-container">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      )}

      {dados && !loading && (
        <>
          {/* ALERTA DE CACHE - Se dados estiverem muito antigos */}
          {dadosMuitoAntigos && (
            <div className="alerta-cache">
              <div className="alerta-icon">⚠️</div>
              <div className="alerta-content">
                <h3>🔥 Dados Desatualizados - Cache do Navegador Detectado!</h3>
                <p>
                  Você está vendo dados de <strong>{formatDate(dados.dados[dados.dados.length - 1]?.data, 'full')}</strong> mas 
                  dados mais recentes estão disponíveis na API.
                </p>
                <div className="alerta-solucoes">
                  <p><strong>Soluções (escolha uma):</strong></p>
                  <ol>
                    <li><strong>Hard Refresh:</strong> Pressione <kbd>Ctrl + Shift + R</kbd> (Windows) ou <kbd>Cmd + Shift + R</kbd> (Mac)</li>
                    <li><strong>Limpar Cache:</strong> Pressione <kbd>Ctrl + Shift + Del</kbd> e limpe "Imagens e arquivos em cache"</li>
                    <li><strong>Modo Anônimo:</strong> Abra uma janela anônima <kbd>Ctrl + Shift + N</kbd></li>
                    <li><strong>Ou clique no botão:</strong> 
                      <button 
                        className="botao-limpar-cache"
                        onClick={() => {
                          setApiVersion(Date.now())
                          setDados(null)
                          buscarCotacoes()
                        }}
                      >
                        🔄 Forçar Atualização
                      </button>
                    </li>
                  </ol>
                </div>
                <p className="alerta-tech">
                  <strong>🔍 Debug:</strong> Abra o Console (F12) para ver os dados reais recebidos da API.
                </p>
              </div>
            </div>
          )}

          {/* Estatísticas Cards */}
          <div className="estatisticas-grid">
            <div className="estatistica-card">
              <div className="estatistica-header">
                <span className="estatistica-label">Preço Inicial</span>
                <Calendar size={18} className="card-icon" />
              </div>
              <span className="estatistica-valor">
                {formatCurrency(dados.estatisticas.preco_inicial)}
              </span>
              <span className="estatistica-data">
                {formatDate(dados.dados[0]?.data, 'full')}
              </span>
            </div>

            <div className="estatistica-card highlight">
              <div className="estatistica-header">
                <span className="estatistica-label">Preço Atual</span>
                <DollarSign size={18} className="card-icon" />
              </div>
              <span className="estatistica-valor primary">
                {formatCurrency(dados.estatisticas.preco_final)}
              </span>
              <span className="estatistica-data data-destaque">
                📅 {dados.intradiario && dados.dados[dados.dados.length - 1]?.hora ? (
                  `${formatDate(dados.dados[dados.dados.length - 1]?.data, 'full')} ${dados.dados[dados.dados.length - 1]?.hora}`
                ) : (
                  formatDate(dados.dados[dados.dados.length - 1]?.data, 'full')
                )}
              </span>
            </div>

            <div className={`estatistica-card variation-card ${getVariationClass(dados.estatisticas.variacao_percentual)}`}>
              <div className="estatistica-header">
                <span className="estatistica-label">Variação</span>
                {dados.estatisticas.variacao_percentual >= 0 ? (
                  <TrendingUp size={18} className="card-icon" />
                ) : (
                  <TrendingDown size={18} className="card-icon" />
                )}
              </div>
              <span className={`estatistica-valor variation ${getVariationClass(dados.estatisticas.variacao_percentual)}`}>
                {formatPercent(dados.estatisticas.variacao_percentual)}
              </span>
              <span className="estatistica-diff">
                {dados.estatisticas.variacao_percentual >= 0 ? '+' : ''}
                {formatCurrency(dados.estatisticas.preco_final - dados.estatisticas.preco_inicial)}
              </span>
            </div>

            <div className="estatistica-card">
              <div className="estatistica-header">
                <span className="estatistica-label">Máxima</span>
                <TrendingUp size={18} className="card-icon" />
              </div>
              <span className="estatistica-valor text-bull">
                {formatCurrency(dados.estatisticas.preco_maximo)}
              </span>
              <span className="estatistica-data">
                No período
              </span>
            </div>

            <div className="estatistica-card">
              <div className="estatistica-header">
                <span className="estatistica-label">Mínima</span>
                <TrendingDown size={18} className="card-icon" />
              </div>
              <span className="estatistica-valor text-bear">
                {formatCurrency(dados.estatisticas.preco_minimo)}
              </span>
              <span className="estatistica-data">
                No período
              </span>
            </div>

            <div className="estatistica-card">
              <div className="estatistica-header">
                <span className="estatistica-label">Volume Médio</span>
                <Activity size={18} className="card-icon" />
              </div>
              <span className="estatistica-valor mono">
                {formatNumber(Math.round(dados.estatisticas.volume_medio))}
              </span>
              <span className="estatistica-data">
                Por dia
              </span>
            </div>
          </div>

          {/* Gráfico Principal */}
          <div className="chart-container main-chart">
            <div className="chart-header">
              <div className="chart-title-section">
                <h4>📊 Evolução do Preço</h4>
                <div className="chart-info">
                  <span className="info-badge">
                    <Activity size={14} />
                    {dados.estatisticas.total_registros} registros
                  </span>
                  <span className="info-badge">
                    <Calendar size={14} />
                    {periodo === '1d' ? '1 dia' : periodo === '5d' ? '5 dias' : periodo === '1mo' ? '1 mês' : periodo === '3mo' ? '3 meses' : periodo === '6mo' ? '6 meses' : periodo === '1y' ? '1 ano' : periodo === '2y' ? '2 anos' : periodo === '5y' ? '5 anos' : 'Histórico completo'}
                  </span>
                </div>
              </div>
              
              <div className="chart-stats">
                <span className="stat-item">
                  <span className="stat-label">Mín:</span>
                  <span className="stat-value text-bear">{formatCurrency(stats.min)}</span>
                </span>
                <span className="stat-item">
                  <span className="stat-label">Méd:</span>
                  <span className="stat-value">{formatCurrency(stats.avg)}</span>
                </span>
                <span className="stat-item">
                  <span className="stat-label">Máx:</span>
                  <span className="stat-value text-bull">{formatCurrency(stats.max)}</span>
                </span>
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={450}>
              {chartType === 'area' ? (
                <AreaChart data={chartDataWithMA} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={CHART_COLORS.bull} stopOpacity={0.4}/>
                      <stop offset="50%" stopColor={CHART_COLORS.bull} stopOpacity={0.2}/>
                      <stop offset="100%" stopColor={CHART_COLORS.bull} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  
                  <CartesianGrid {...defaultGridStyle} />
                  
                  <XAxis
                    dataKey="dateFormatted"
                    {...defaultAxisStyle}
                    interval="preserveStartEnd"
                    minTickGap={60}
                  />
                  
                  <YAxis
                    domain={domain}
                    {...defaultAxisStyle}
                    tickFormatter={(value) => formatCurrency(value)}
                    width={80}
                  />
                  
                  {/* Linha de referência da média */}
                  <ReferenceLine 
                    y={stats.avg} 
                    stroke={CHART_COLORS.cyan}
                    strokeDasharray="5 5"
                    label={{ 
                      value: `Média: ${formatCurrency(stats.avg)}`, 
                      fill: CHART_COLORS.cyan,
                      fontSize: 12,
                      position: 'insideTopRight'
                    }}
                  />
                  
                  <Tooltip
                    {...defaultTooltipStyle}
                    formatter={(value, name) => {
                      if (name === 'value') return [formatCurrency(value), 'Preço']
                      if (name === 'media') return [formatCurrency(value), 'Média Móvel (20)']
                      return [value, name]
                    }}
                    labelFormatter={(label) => `Data: ${label}`}
                  />
                  
                  {/* Média móvel (apenas para dados diários) */}
                  {!isIntraday && (
                    <Line
                      type="monotone"
                      dataKey="media"
                      stroke={CHART_COLORS.gold}
                      strokeWidth={2}
                      dot={false}
                      strokeDasharray="3 3"
                      opacity={0.6}
                    />
                  )}
                  
                  {/* Área principal */}
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={CHART_COLORS.bull}
                    strokeWidth={3}
                    fill="url(#colorPrice)"
                    activeDot={{
                      r: 8,
                      fill: CHART_COLORS.bull,
                      stroke: '#fff',
                      strokeWidth: 3,
                      filter: 'drop-shadow(0 0 6px rgba(16, 185, 129, 0.8))'
                    }}
                  />
                </AreaChart>
              ) : (
                <LineChart data={chartDataWithMA} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
                  <CartesianGrid {...defaultGridStyle} strokeDasharray="3 3" />
                  
                  <XAxis
                    dataKey="dateFormatted"
                    {...defaultAxisStyle}
                    interval={isIntraday ? 'preserveStartEnd' : 'preserveStartEnd'}
                    minTickGap={isIntraday ? 30 : 60}
                    angle={isIntraday ? -45 : 0}
                    textAnchor={isIntraday ? 'end' : 'middle'}
                    height={isIntraday ? 80 : 30}
                  />
                  
                  <YAxis
                    domain={domain}
                    {...defaultAxisStyle}
                    tickFormatter={(value) => formatCurrency(value)}
                    width={80}
                  />
                  
                  {/* Linha de referência da média */}
                  <ReferenceLine 
                    y={stats.avg} 
                    stroke={CHART_COLORS.cyan}
                    strokeDasharray="5 5"
                    label={{ 
                      value: `Média: ${formatCurrency(stats.avg)}`, 
                      fill: CHART_COLORS.cyan,
                      fontSize: 12,
                      position: 'insideTopRight'
                    }}
                  />
                  
                  <Tooltip
                    {...defaultTooltipStyle}
                    formatter={(value, name) => {
                      if (name === 'value') return [formatCurrency(value), isIntraday ? 'Preço' : 'Fechamento']
                      if (name === 'media') return [formatCurrency(value), 'Média Móvel (20)']
                      return [value, name]
                    }}
                    labelFormatter={(label) => isIntraday ? `Hora: ${label}` : `Data: ${label}`}
                  />
                  
                  {/* Média móvel (apenas para dados diários) */}
                  {!isIntraday && (
                    <Line
                      type="monotone"
                      dataKey="media"
                      stroke={CHART_COLORS.gold}
                      strokeWidth={2}
                      dot={false}
                      strokeDasharray="3 3"
                    />
                  )}
                  
                  {/* Linha principal */}
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={CHART_COLORS.bull}
                    strokeWidth={3}
                    dot={false}
                    activeDot={{
                      r: 8,
                      fill: CHART_COLORS.bull,
                      stroke: '#fff',
                      strokeWidth: 3,
                      filter: 'drop-shadow(0 0 6px rgba(16, 185, 129, 0.8))'
                    }}
                  />
                </LineChart>
              )}
            </ResponsiveContainer>

            {/* Legenda do Gráfico */}
            <div className="chart-legend">
              <div className="legend-item">
                <span className="legend-dot" style={{ background: CHART_COLORS.bull }}></span>
                <span>{isIntraday ? 'Preço Intradiário (5min)' : 'Preço de Fechamento'}</span>
              </div>
              {!isIntraday && (
                <div className="legend-item">
                  <span className="legend-line" style={{ borderColor: CHART_COLORS.gold }}></span>
                  <span>Média Móvel (20 dias)</span>
                </div>
              )}
              <div className="legend-item">
                <span className="legend-line dashed" style={{ borderColor: CHART_COLORS.cyan }}></span>
                <span>Média do {isIntraday ? 'Dia' : 'Período'}</span>
              </div>
              {isIntraday && (
                <div className="legend-item">
                  <span className="legend-info">⏱️</span>
                  <span>Dados a cada 5 minutos</span>
                </div>
              )}
            </div>
          </div>

          {/* Análise Técnica Rápida */}
          <div className="analise-rapida">
            <h4>🎯 Análise Técnica Rápida</h4>
            <div className="analise-grid">
              <div className="analise-item">
                <div className="analise-icon">📊</div>
                <div className="analise-content">
                  <span className="analise-label">Tendência</span>
                  <span className={`analise-value ${dados.estatisticas.variacao_percentual >= 0 ? 'positive' : 'negative'}`}>
                    {dados.estatisticas.variacao_percentual >= 0 ? '🟢 Alta' : '🔴 Baixa'}
                  </span>
                </div>
              </div>

              <div className="analise-item">
                <div className="analise-icon">💹</div>
                <div className="analise-content">
                  <span className="analise-label">Amplitude</span>
                  <span className="analise-value">
                    {formatCurrency(dados.estatisticas.preco_maximo - dados.estatisticas.preco_minimo)}
                  </span>
                </div>
              </div>

              <div className="analise-item">
                <div className="analise-icon">📈</div>
                <div className="analise-content">
                  <span className="analise-label">Variação Absoluta</span>
                  <span className={`analise-value ${dados.estatisticas.variacao_percentual >= 0 ? 'positive' : 'negative'}`}>
                    {dados.estatisticas.variacao_percentual >= 0 ? '+' : ''}
                    {formatCurrency(dados.estatisticas.preco_final - dados.estatisticas.preco_inicial)}
                  </span>
                </div>
              </div>

              <div className="analise-item">
                <div className="analise-icon">📊</div>
                <div className="analise-content">
                  <span className="analise-label">Volatilidade</span>
                  <span className="analise-value">
                    {(((dados.estatisticas.preco_maximo - dados.estatisticas.preco_minimo) / stats.avg) * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Análise de Horários */}
          {analiseHorarios && !loadingHorarios && (
            <div className="analise-horarios">
              <div className="horarios-header">
                <h4>⏰ Análise de Horários - Últimos 30 Dias</h4>
                <span className="horarios-badge">
                  {analiseHorarios.total_registros} registros analisados
                </span>
              </div>
              
              {/* Estatísticas Principais */}
              <div className="horarios-destaque">
                <div className="horario-card compra">
                  <div className="horario-icon">🟢 MELHOR COMPRA</div>
                  <div className="horario-info">
                    <span className="horario-tempo">
                      {analiseHorarios.recomendacao.melhor_horario_compra?.hora}
                    </span>
                    <span className="horario-preco">
                      {formatCurrency(analiseHorarios.recomendacao.melhor_horario_compra?.preco_medio)}
                    </span>
                    <span className="horario-detalhe">
                      Preço médio mais baixo ({analiseHorarios.recomendacao.melhor_horario_compra?.ocorrencias}x observado)
                    </span>
                  </div>
                </div>

                <div className="horario-card venda">
                  <div className="horario-icon">🔴 MELHOR VENDA</div>
                  <div className="horario-info">
                    <span className="horario-tempo">
                      {analiseHorarios.recomendacao.melhor_horario_venda?.hora}
                    </span>
                    <span className="horario-preco">
                      {formatCurrency(analiseHorarios.recomendacao.melhor_horario_venda?.preco_medio)}
                    </span>
                    <span className="horario-detalhe">
                      Preço médio mais alto ({analiseHorarios.recomendacao.melhor_horario_venda?.ocorrencias}x observado)
                    </span>
                  </div>
                </div>

                <div className="horario-card diferenca">
                  <div className="horario-icon">💰 DIFERENÇA</div>
                  <div className="horario-info">
                    <span className="horario-tempo">
                      {analiseHorarios.recomendacao.diferenca_percentual >= 0 ? '+' : ''}
                      {analiseHorarios.recomendacao.diferenca_percentual}%
                    </span>
                    <span className="horario-preco">
                      {formatCurrency(
                        analiseHorarios.recomendacao.melhor_horario_venda?.preco_medio - 
                        analiseHorarios.recomendacao.melhor_horario_compra?.preco_medio
                      )}
                    </span>
                    <span className="horario-detalhe">
                      Potencial entre compra e venda
                    </span>
                  </div>
                </div>
              </div>

              {/* Top 5 Horários */}
              <div className="horarios-rankings">
                {/* Melhores para Compra */}
                <div className="ranking-section">
                  <h5>📉 Top 5 Horários - Menores Preços (Compra)</h5>
                  <div className="ranking-list">
                    {analiseHorarios.melhores_horarios_compra.map((h, idx) => (
                      <div key={idx} className="ranking-item compra">
                        <span className="ranking-pos">{idx + 1}º</span>
                        <span className="ranking-hora">{h.hora}</span>
                        <span className="ranking-preco">{formatCurrency(h.preco_medio)}</span>
                        <span className="ranking-info">
                          {h.ocorrencias}x | Vol: {formatNumber(h.volume_medio)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Melhores para Venda */}
                <div className="ranking-section">
                  <h5>📈 Top 5 Horários - Maiores Preços (Venda)</h5>
                  <div className="ranking-list">
                    {analiseHorarios.melhores_horarios_venda.map((h, idx) => (
                      <div key={idx} className="ranking-item venda">
                        <span className="ranking-pos">{idx + 1}º</span>
                        <span className="ranking-hora">{h.hora}</span>
                        <span className="ranking-preco">{formatCurrency(h.preco_medio)}</span>
                        <span className="ranking-info">
                          {h.ocorrencias}x | Vol: {formatNumber(h.volume_medio)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Aviso */}
              <div className="horarios-aviso">
                💡 <strong>Atenção:</strong> Esta análise é baseada em dados históricos dos últimos 30 dias. 
                Padrões passados não garantem resultados futuros. Use como referência, não como regra absoluta.
              </div>
            </div>
          )}

          {/* Tabela de Histórico */}
          <div className="cotacoes-table-container">
            <div className="table-header-section">
              <h4>📜 Histórico Detalhado</h4>
              <span className="table-count">{dados.estatisticas.total_registros} registros</span>
            </div>
            <div className="cotacoes-table">
              <div className="table-header">
                <span>Data</span>
                <span>Abertura</span>
                <span>Fechamento</span>
                <span>Máxima</span>
                <span>Mínima</span>
                <span>Volume</span>
              </div>
              {dados.dados.slice().reverse().slice(0, 100).map((item, index) => (
                <div key={index} className="table-row">
                  <span className="table-date">
                    {formatDate(item.data, 'full')}
                  </span>
                  <span className="mono">{formatCurrency(item.abertura)}</span>
                  <span className="mono highlight">{formatCurrency(item.fechamento)}</span>
                  <span className="mono text-bull">{formatCurrency(item.maxima)}</span>
                  <span className="mono text-bear">{formatCurrency(item.minima)}</span>
                  <span className="mono volume">{formatNumber(item.volume)}</span>
                </div>
              ))}
            </div>
            {dados.dados.length > 100 && (
              <div className="table-info">
                💡 Mostrando os 100 registros mais recentes de {dados.estatisticas.total_registros}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

CotacoesTab.propTypes = {
  ticker: PropTypes.string
}

export default CotacoesTab
