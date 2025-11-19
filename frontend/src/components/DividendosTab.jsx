import { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'
import { DollarSign, TrendingUp, TrendingDown, Calendar, Percent, Activity } from 'lucide-react'
import { formatDate as formatDateUtil } from '../utils/chartUtils'
import './DividendosTab.css'

// Funções auxiliares locais
const formatCurrency = (value) => {
  if (value == null || isNaN(value)) return 'R$ 0,00'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

// NOTA: Este endpoint retorna dividend_yield em DECIMAL (0.1245 = 12.45%)
// Diferente de outros endpoints que já normalizam para percentual
const formatPercent = (value) => {
  if (value == null || isNaN(value)) return '0.00%'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// Usa a função corrigida do chartUtils (com fix de timezone)
const formatDate = (dateStr) => {
  return formatDateUtil(dateStr, 'full')
}

const CHART_COLORS = {
  bull: '#10b981',
  cyan: '#06b6d4',
  gridLine: '#334155',
  axisText: '#cbd5e1',
  tooltipBg: '#1e293b',
  tooltipBorder: '#475569'
}

function DividendosTab({ ticker }) {
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [periodo, setPeriodo] = useState('12m')

  useEffect(() => {
    if (ticker) {
      buscarDividendos()
    }
  }, [ticker])

  const buscarDividendos = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `http://localhost:5001/api/fii/${ticker}/dividendos`
      )

      if (!response.ok) {
        throw new Error('Erro ao buscar dividendos')
      }

      const data = await response.json()
      console.log('Dados recebidos:', data)
      setDados(data)
    } catch (err) {
      setError(err.message)
      console.error('Erro ao buscar dividendos:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!ticker) {
    return (
      <div className="dividendos-tab">
        <div className="empty-state">
          <div className="empty-icon">💰</div>
          <h3>Selecione um FII</h3>
          <p>Busque um fundo para visualizar o histórico de dividendos</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="dividendos-tab">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando dividendos...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dividendos-tab">
        <div className="error-container">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  if (!dados || !dados.dividendos || dados.dividendos.length === 0) {
    return (
      <div className="dividendos-tab">
        <div className="empty-state">
          <div className="empty-icon">💰</div>
          <h3>Sem Dividendos</h3>
          <p>Nenhum dividendo encontrado para {ticker}</p>
        </div>
      </div>
    )
  }

  // Filtrar dados por período
  const getFilteredData = () => {
    if (!dados || !dados.dividendos) return []
    
    const now = new Date()
    let startDate = new Date()
    
    switch(periodo) {
      case '6m':
        startDate.setMonth(now.getMonth() - 6)
        break
      case '12m':
        startDate.setMonth(now.getMonth() - 12)
        break
      case '24m':
        startDate.setMonth(now.getMonth() - 24)
        break
      case 'all':
      default:
        return dados.dividendos
    }
    
    return dados.dividendos.filter(d => {
      try {
        return new Date(d.data_pagamento) >= startDate
      } catch (e) {
        return true
      }
    })
  }

  const filteredData = getFilteredData()
  
  // Processa dados para o gráfico
  const chartData = filteredData.map(item => ({
    date: item.data_pagamento,
    value: item.valor,
    dateFormatted: formatDate(item.data_pagamento)
  })).sort((a, b) => new Date(a.date) - new Date(b.date))
  
  // Calcula estatísticas
  const values = chartData.map(d => d.value).filter(v => v != null && !isNaN(v))
  const stats = {
    min: values.length > 0 ? Math.min(...values) : 0,
    max: values.length > 0 ? Math.max(...values) : 0,
    avg: values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0,
    total: values.length > 0 ? values.reduce((a, b) => a + b, 0) : 0,
    count: values.length
  }
  
  // Domínio do gráfico - sempre do zero até max + 10%
  const domain = [0, stats.max > 0 ? stats.max * 1.1 : 1]

  const periodos = [
    { value: '6m', label: '6 Meses' },
    { value: '12m', label: '12 Meses' },
    { value: '24m', label: '24 Meses' },
    { value: 'all', label: 'Tudo' }
  ]

  return (
    <div className="dividendos-tab">
      <div className="dividendos-header">
        <div className="header-title-section">
          <h3 className="dividendos-title">
            <DollarSign size={28} />
            Histórico de Dividendos
          </h3>
          <span className="ticker-badge">{ticker.replace('.SA', '')}</span>
        </div>

        <div className="periodo-selector">
          {periodos.map((p) => (
            <button
              key={p.value}
              className={`periodo-button ${periodo === p.value ? 'active' : ''}`}
              onClick={() => setPeriodo(p.value)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Estatísticas Cards */}
      <div className="estatisticas-grid">
        <div className="estatistica-card highlight">
          <div className="estatistica-header">
            <span className="estatistica-label">Dividend Yield</span>
            <Percent size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor primary">
            {dados.dividend_yield ? formatPercent(dados.dividend_yield * 100) : 'N/A'}
          </span>
          <span className="estatistica-info">Anualizado (12M)</span>
        </div>

        <div className="estatistica-card">
          <div className="estatistica-header">
            <span className="estatistica-label">Total Pago</span>
            <DollarSign size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor">
            {formatCurrency(stats.total)}
          </span>
          <span className="estatistica-info">No período</span>
        </div>

        <div className="estatistica-card">
          <div className="estatistica-header">
            <span className="estatistica-label">Média por Pagamento</span>
            <TrendingUp size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor">
            {formatCurrency(stats.avg)}
          </span>
          <span className="estatistica-info">Média</span>
        </div>

        <div className="estatistica-card">
          <div className="estatistica-header">
            <span className="estatistica-label">Maior Pagamento</span>
            <TrendingUp size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor text-bull">
            {formatCurrency(stats.max)}
          </span>
          <span className="estatistica-info">Máximo</span>
        </div>

        <div className="estatistica-card">
          <div className="estatistica-header">
            <span className="estatistica-label">Menor Pagamento</span>
            <TrendingDown size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor text-bear">
            {formatCurrency(stats.min)}
          </span>
          <span className="estatistica-info">Mínimo</span>
        </div>

        <div className="estatistica-card">
          <div className="estatistica-header">
            <span className="estatistica-label">Total de Pagamentos</span>
            <Calendar size={18} className="card-icon" />
          </div>
          <span className="estatistica-valor mono">
            {stats.count}
          </span>
          <span className="estatistica-info">Registros</span>
        </div>
      </div>

      {/* Gráfico de Barras */}
      {chartData.length > 0 && (
        <div className="chart-container main-chart">
          <div className="chart-header">
            <h4>📊 Evolução dos Dividendos</h4>
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

          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 60 }}>
              <CartesianGrid stroke={CHART_COLORS.gridLine} strokeDasharray="3 3" opacity={0.3} />

              <XAxis
                dataKey="dateFormatted"
                tick={{ fill: CHART_COLORS.axisText, fontSize: 11 }}
                axisLine={{ stroke: CHART_COLORS.gridLine }}
                tickLine={{ stroke: CHART_COLORS.gridLine }}
                interval="preserveStartEnd"
                minTickGap={40}
                angle={-45}
                textAnchor="end"
                height={80}
              />

              <YAxis
                domain={domain}
                tick={{ fill: CHART_COLORS.axisText, fontSize: 12 }}
                axisLine={{ stroke: CHART_COLORS.gridLine }}
                tickLine={{ stroke: CHART_COLORS.gridLine }}
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
                contentStyle={{
                  backgroundColor: CHART_COLORS.tooltipBg,
                  border: `1px solid ${CHART_COLORS.tooltipBorder}`,
                  borderRadius: '12px',
                  padding: '12px 16px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)'
                }}
                labelStyle={{
                  color: CHART_COLORS.axisText,
                  fontWeight: '600',
                  marginBottom: '8px'
                }}
                itemStyle={{
                  color: CHART_COLORS.axisText,
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '14px'
                }}
                formatter={(value) => [formatCurrency(value), 'Dividendo']}
                labelFormatter={(label) => `Data: ${label}`}
              />

              <Bar
                dataKey="value"
                radius={[8, 8, 0, 0]}
                maxBarSize={60}
              >
                {chartData.map((entry, index) => {
                  // Calcula opacity baseado no valor (maior = mais opaco)
                  const opacity = stats.max > 0 ? 0.6 + (entry.value / stats.max) * 0.4 : 0.8
                  
                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_COLORS.bull}
                      opacity={opacity}
                    />
                  )
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          
          {/* Legenda do Gráfico */}
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-dot" style={{ background: CHART_COLORS.bull }}></span>
              <span>Dividendos Pagos</span>
            </div>
            <div className="legend-item">
              <span className="legend-line dashed" style={{ borderColor: CHART_COLORS.cyan }}></span>
              <span>Média ({formatCurrency(stats.avg)})</span>
            </div>
            <div className="legend-item">
              <span className="legend-info">💡</span>
              <span>Barras mais escuras = valores maiores</span>
            </div>
          </div>
        </div>
      )}

      {/* Tabela de Dividendos */}
      <div className="dividendos-table-container">
        <div className="table-header-section">
          <h4>📜 Histórico Detalhado</h4>
          <span className="table-count">{filteredData.length} pagamentos</span>
        </div>
        <div className="dividendos-table">
          <div className="table-header">
            <span>Data Com</span>
            <span>Data Pagamento</span>
            <span>Valor</span>
            <span>Tipo</span>
          </div>
          {filteredData.slice().reverse().map((item, index) => (
            <div key={index} className="table-row">
              <span className="table-date">
                {formatDate(item.data_com)}
              </span>
              <span className="table-date">
                {formatDate(item.data_pagamento)}
              </span>
              <span className="mono highlight">
                {formatCurrency(item.valor)}
              </span>
              <span className="tipo-badge">
                {item.tipo || 'Rendimento'}
              </span>
            </div>
          ))}
        </div>
        {filteredData.length === 0 && (
          <div className="empty-table">
            <p>💡 Nenhum dividendo encontrado no período selecionado</p>
          </div>
        )}
      </div>
    </div>
  )
}

DividendosTab.propTypes = {
  ticker: PropTypes.string
}

export default DividendosTab
