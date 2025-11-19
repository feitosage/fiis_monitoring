import PropTypes from 'prop-types'
import { formatDate } from '../utils/chartUtils'
import './FIIDetail.css'

function FIIDetail({ fii }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  // Formata VARIAÇÃO (backend envia em decimal: -0.10373681 = -10.37%)
  const formatVariacao = (value) => {
    if (value == null || isNaN(value)) return '0.00%'
    const percentValue = value * 100
    const sign = percentValue >= 0 ? '+' : ''
    return `${sign}${percentValue.toFixed(2)}%`
  }

  // Formata DIVIDEND YIELD (backend já envia em %: 12.45 = 12.45%)
  const formatDY = (value) => {
    if (value == null || isNaN(value)) return '0.00%'
    return `${value.toFixed(2)}%`
  }

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value)
  }

  return (
    <div className="fii-detail">
      <div className="detail-header">
        <h3>{fii.ticker.replace('.SA', '')}</h3>
        <p className="detail-name">{fii.nome}</p>
      </div>

      <div className="detail-grid">
        <div className="detail-item">
          <span className="detail-label">Preço Atual</span>
          <span className="detail-value highlight">{formatCurrency(fii.preco_atual)}</span>
        </div>

        <div className="detail-item">
          <span className="detail-label">Variação do Dia</span>
          <span className={`detail-value ${fii.variacao_dia >= 0 ? 'positive' : 'negative'}`}>
            {formatVariacao(fii.variacao_dia)}
          </span>
        </div>

        {fii.dividend_yield > 0 && (
          <div className="detail-item">
            <span className="detail-label">Dividend Yield</span>
            <span className="detail-value">{formatDY(fii.dividend_yield)}</span>
          </div>
        )}

        <div className="detail-item">
          <span className="detail-label">Volume</span>
          <span className="detail-value">
            {formatNumber(fii.volume)}
            {fii.volume_data && fii.volume_data !== 'hoje' && (
              <span className="volume-date"> ({fii.volume_data})</span>
            )}
          </span>
          {fii.volume === 0 && (
            <span className="alert-badge">⚠️ Baixa liquidez</span>
          )}
        </div>

        <div className="detail-item">
          <span className="detail-label">Mínima 52 Semanas</span>
          <span className="detail-value">{formatCurrency(fii.minima_52_semanas)}</span>
        </div>

        <div className="detail-item">
          <span className="detail-label">Máxima 52 Semanas</span>
          <span className="detail-value">{formatCurrency(fii.maxima_52_semanas)}</span>
        </div>
      </div>

      {fii.historico && fii.historico.length > 0 && (
        <div className="detail-history">
          <h4>Histórico (Últimos 30 dias)</h4>
          <div className="history-table">
            <div className="history-header">
              <span>Data</span>
              <span>Fechamento</span>
              <span>Volume</span>
            </div>
            {fii.historico.slice(-10).reverse().map((item, index) => (
              <div key={index} className="history-row">
                <span>{formatDate(item.data, 'full')}</span>
                <span>{formatCurrency(item.fechamento)}</span>
                <span>{formatNumber(item.volume)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

FIIDetail.propTypes = {
  fii: PropTypes.shape({
    ticker: PropTypes.string.isRequired,
    nome: PropTypes.string.isRequired,
    preco_atual: PropTypes.number.isRequired,
    variacao_dia: PropTypes.number.isRequired,
    dividend_yield: PropTypes.number,
    volume: PropTypes.number.isRequired,
    minima_52_semanas: PropTypes.number.isRequired,
    maxima_52_semanas: PropTypes.number.isRequired,
    historico: PropTypes.arrayOf(PropTypes.shape({
      data: PropTypes.string.isRequired,
      fechamento: PropTypes.number.isRequired,
      volume: PropTypes.number.isRequired
    }))
  }).isRequired
}

export default FIIDetail

