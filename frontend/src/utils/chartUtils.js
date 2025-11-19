/**
 * 📊 CHART UTILITIES - Smart Chart Configuration
 * Funções utilitárias para gráficos otimizados e profissionais
 */

// ═══════════════════════════════════════════════════════════════
// 🎨 COLORS - Investment Theme
// ═══════════════════════════════════════════════════════════════

export const CHART_COLORS = {
  // Bull Market (Positive)
  bull: '#10b981',
  bullDark: '#059669',
  bullLight: '#34d399',
  
  // Bear Market (Negative)
  bear: '#dc2626',
  bearDark: '#b91c1c',
  bearLight: '#ef4444',
  
  // Neutral & Accents
  cyan: '#06b6d4',
  purple: '#8b5cf6',
  gold: '#f59e0b',
  
  // UI Colors
  gridLine: '#334155',
  axisText: '#cbd5e1',
  tooltipBg: '#1e293b',
  tooltipBorder: '#475569'
}

// ═══════════════════════════════════════════════════════════════
// 📈 DOMAIN CALCULATORS - Smart Y-Axis Scaling
// ═══════════════════════════════════════════════════════════════

/**
 * Calcula domínio otimizado para preços (não começa do zero)
 * @param {Array} data - Array de dados
 * @param {string} key - Chave do valor no objeto
 * @returns {Array} [min, max]
 */
export function calculatePriceDomain(data, key = 'value') {
  if (!data || data.length === 0) return [0, 100]
  
  const values = data.map(item => item[key]).filter(v => v != null && !isNaN(v))
  if (values.length === 0) return [0, 100]
  
  const min = Math.min(...values)
  const max = Math.max(...values)
  
  // Margem de 2% para baixo e 2% para cima
  const margin = (max - min) * 0.02
  
  return [
    Math.max(0, min - margin),
    max + margin
  ]
}

/**
 * Calcula domínio para percentuais (permite negativos, margem proporcional)
 * @param {Array} data - Array de dados
 * @param {string} key - Chave do valor no objeto
 * @returns {Array} [min, max]
 */
export function calculatePercentageDomain(data, key = 'value') {
  if (!data || data.length === 0) return [-5, 5]
  
  const values = data.map(item => item[key]).filter(v => v != null && !isNaN(v))
  if (values.length === 0) return [-5, 5]
  
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min
  
  // Margem proporcional ao range (mínimo 10% do range ou 1)
  const margin = Math.max(range * 0.1, 1)
  
  return [
    min - margin,
    max + margin
  ]
}

/**
 * Calcula domínio para dividendos (sempre começa do zero)
 * @param {Array} data - Array de dados
 * @param {string} key - Chave do valor no objeto
 * @returns {Array} [min, max]
 */
export function calculateDividendDomain(data, key = 'value') {
  if (!data || data.length === 0) return [0, 10]
  
  const values = data.map(item => item[key]).filter(v => v != null && !isNaN(v))
  if (values.length === 0) return [0, 10]
  
  const max = Math.max(...values)
  
  // Sempre começa do zero, margem de 10% no topo
  return [0, max * 1.1]
}

/**
 * Calcula domínio para OHLC (considera todos os valores: open, high, low, close)
 * @param {Array} data - Array de dados OHLC
 * @returns {Array} [min, max]
 */
export function calculateOHLCDomain(data) {
  if (!data || data.length === 0) return [0, 100]
  
  const allValues = data.flatMap(item => [
    item.abertura,
    item.maxima,
    item.minima,
    item.fechamento
  ]).filter(v => v != null && !isNaN(v))
  
  if (allValues.length === 0) return [0, 100]
  
  const min = Math.min(...allValues)
  const max = Math.max(...allValues)
  
  // Range ultra-otimizado para análise técnica (0.5% margem)
  const margin = (max - min) * 0.005
  
  return [
    Math.max(0, min - margin),
    max + margin
  ]
}

// ═══════════════════════════════════════════════════════════════
// 🎨 FORMATTERS - Data Formatting
// ═══════════════════════════════════════════════════════════════

/**
 * Formata valores monetários (BRL)
 */
export function formatCurrency(value) {
  if (value == null || isNaN(value)) return 'R$ 0,00'
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

/**
 * Formata percentuais
 */
export function formatPercent(value, decimals = 2) {
  if (value == null || isNaN(value)) return '0.00%'
  
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

/**
 * Formata números grandes (volume, etc)
 */
export function formatNumber(value) {
  if (value == null || isNaN(value)) return '0'
  
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(2)}B`
  } else if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`
  } else if (value >= 1_000) {
    return `${(value / 1_000).toFixed(2)}K`
  }
  
  return new Intl.NumberFormat('pt-BR').format(value)
}

/**
 * Formata datas (corrigido para timezone)
 */
export function formatDate(date, format = 'short') {
  if (!date) return ''
  
  // FIX: Adiciona 'T12:00:00' para evitar problema de timezone
  // Quando a data vem como "2025-10-22", JS assume meia-noite UTC
  // No timezone BR (-3h), isso vira 21/10 às 21h
  let dateStr = date
  if (typeof date === 'string' && date.match(/^\d{4}-\d{2}-\d{2}$/)) {
    // Data no formato YYYY-MM-DD sem hora
    dateStr = date + 'T12:00:00' // Meio-dia no horário local
  }
  
  const d = new Date(dateStr)
  
  if (format === 'short') {
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    })
  }
  
  if (format === 'medium') {
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  }
  
  if (format === 'chart') {
    return d.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: '2-digit'
    })
  }
  
  // Para formato 'full', força usar a data exata sem conversão de timezone
  if (format === 'full') {
    // Extrai ano, mês e dia diretamente da string
    if (typeof date === 'string' && date.match(/^\d{4}-\d{2}-\d{2}/)) {
      const [ano, mes, dia] = date.split('T')[0].split('-')
      return `${dia}/${mes}/${ano}`
    }
  }
  
  return d.toLocaleDateString('pt-BR')
}

// ═══════════════════════════════════════════════════════════════
// 🎯 CHART CONFIGS - Recharts Configurations
// ═══════════════════════════════════════════════════════════════

/**
 * Configuração padrão do Tooltip
 */
export const defaultTooltipStyle = {
  contentStyle: {
    backgroundColor: CHART_COLORS.tooltipBg,
    border: `1px solid ${CHART_COLORS.tooltipBorder}`,
    borderRadius: '12px',
    padding: '12px 16px',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(10px)'
  },
  labelStyle: {
    color: CHART_COLORS.axisText,
    fontWeight: '600',
    marginBottom: '8px'
  },
  itemStyle: {
    color: CHART_COLORS.axisText,
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: '14px'
  },
  cursor: {
    fill: 'rgba(16, 185, 129, 0.1)'
  }
}

/**
 * Configuração padrão do Grid
 */
export const defaultGridStyle = {
  stroke: CHART_COLORS.gridLine,
  strokeDasharray: '3 3',
  opacity: 0.3
}

/**
 * Configuração padrão dos Eixos
 */
export const defaultAxisStyle = {
  tick: {
    fill: CHART_COLORS.axisText,
    fontSize: 12,
    fontFamily: 'JetBrains Mono, monospace'
  },
  axisLine: {
    stroke: CHART_COLORS.gridLine
  },
  tickLine: {
    stroke: CHART_COLORS.gridLine
  }
}

/**
 * Retorna a cor baseado no valor (bull/bear)
 */
export function getValueColor(value) {
  if (value > 0) return CHART_COLORS.bull
  if (value < 0) return CHART_COLORS.bear
  return CHART_COLORS.axisText
}

/**
 * Retorna o gradiente para linha de preço
 */
export function getPriceGradient(id = 'priceGradient') {
  return {
    id,
    stops: [
      { offset: '0%', color: CHART_COLORS.bull, opacity: 0.8 },
      { offset: '100%', color: CHART_COLORS.cyan, opacity: 0.3 }
    ]
  }
}

// ═══════════════════════════════════════════════════════════════
// 📊 DATA PROCESSORS - Process Chart Data
// ═══════════════════════════════════════════════════════════════

/**
 * Processa dados históricos para gráfico de linha
 */
export function processHistoricalData(data, valueKey = 'fechamento') {
  if (!data || !Array.isArray(data)) return []
  
  return data.map(item => ({
    date: item.data,
    value: item[valueKey],
    dateFormatted: formatDate(item.data, 'chart')
  })).sort((a, b) => new Date(a.date) - new Date(b.date))
}

/**
 * Processa dados de dividendos para gráfico de barras
 */
export function processDividendData(data) {
  if (!data || !Array.isArray(data)) return []
  
  return data.map(item => ({
    date: item.data_pagamento || item.data,
    value: item.valor || 0,
    dateFormatted: formatDate(item.data_pagamento || item.data, 'medium')
  })).sort((a, b) => new Date(a.date) - new Date(b.date))
}

/**
 * Calcula estatísticas básicas dos dados
 */
export function calculateStats(data, key = 'value') {
  if (!data || data.length === 0) {
    return {
      min: 0,
      max: 0,
      avg: 0,
      total: 0,
      count: 0
    }
  }
  
  const values = data.map(item => item[key]).filter(v => v != null && !isNaN(v))
  
  if (values.length === 0) {
    return {
      min: 0,
      max: 0,
      avg: 0,
      total: 0,
      count: 0
    }
  }
  
  const sum = values.reduce((a, b) => a + b, 0)
  
  return {
    min: Math.min(...values),
    max: Math.max(...values),
    avg: sum / values.length,
    total: sum,
    count: values.length
  }
}

