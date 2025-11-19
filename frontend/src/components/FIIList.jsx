import PropTypes from 'prop-types'
import './FIIList.css'

function FIIList({ fiis, onSelectFII, selectedTicker, showRemoveButton = false, onRemoveFII }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  // Formata VARIAÇÃO (backend envia em decimal: -0.10373681 = -10.37%)
  const formatVariacao = (value) => {
    const formatted = (value * 100).toFixed(2)
    const sign = value >= 0 ? '+' : ''
    return `${sign}${formatted}%`
  }

  // Formata DIVIDEND YIELD (backend já envia em %: 12.45 = 12.45%)
  const formatDY = (value) => {
    if (value == null || isNaN(value)) return '0.00%'
    return `${value.toFixed(2)}%`
  }

  const getVariationClass = (value) => {
    if (value > 0) return 'positive'
    if (value < 0) return 'negative'
    return 'neutral'
  }
  
  const formatSearchTime = (isoDate) => {
    if (!isoDate) return ''
    
    const data = new Date(isoDate)
    const agora = new Date()
    const diffMs = agora - data
    const diffMinutos = Math.floor(diffMs / 60000)
    
    if (diffMinutos < 1) return 'Agora'
    if (diffMinutos === 1) return 'Há 1 min'
    if (diffMinutos < 60) return `Há ${diffMinutos} min`
    
    const diffHoras = Math.floor(diffMinutos / 60)
    if (diffHoras === 1) return 'Há 1h'
    if (diffHoras < 24) return `Há ${diffHoras}h`
    
    const diffDias = Math.floor(diffHoras / 24)
    if (diffDias === 1) return 'Ontem'
    if (diffDias < 7) return `Há ${diffDias}d`
    
    return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  }

  if (fiis.length === 0) {
    return <div className="empty-list">Nenhum FII encontrado</div>
  }

  return (
    <div className="fii-list">
      {fiis.map((fii) => (
        <div
          key={fii.ticker}
          className={`fii-card ${selectedTicker === fii.ticker.replace('.SA', '') ? 'selected' : ''}`}
          onClick={() => onSelectFII(fii.ticker.replace('.SA', ''))}
        >
          <div className="fii-card-header">
            <div className="fii-card-title">
              <h3>{fii.ticker.replace('.SA', '')}</h3>
              {fii.searchedAt && (
                <span className="search-time" title={new Date(fii.searchedAt).toLocaleString('pt-BR')}>
                  🕐 {formatSearchTime(fii.searchedAt)}
                </span>
              )}
            </div>
            <div className="fii-card-actions">
              <span className={`variation ${getVariationClass(fii.variacao_dia)}`}>
                {formatVariacao(fii.variacao_dia)}
              </span>
              {showRemoveButton && onRemoveFII && (
                <button 
                  className="remove-fii-btn"
                  onClick={(e) => onRemoveFII(fii.ticker, e)}
                  title="Remover do histórico"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          
          <div className="fii-card-body">
            <p className="fii-name">{fii.nome}</p>
            <div className="fii-price">
              <span className="price-label">Preço:</span>
              <span className="price-value">{formatCurrency(fii.preco_atual)}</span>
            </div>
            {fii.dividend_yield > 0 && (
              <div className="fii-dividend">
                <span className="dividend-label">Dividend Yield:</span>
                <span className="dividend-value">{formatDY(fii.dividend_yield)}</span>
              </div>
            )}
            {fii.volume === 0 && (
              <div className="fii-alert">
                <span className="alert-icon">⚠️</span>
                <span className="alert-text">Volume baixo</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

FIIList.propTypes = {
  fiis: PropTypes.arrayOf(PropTypes.shape({
    ticker: PropTypes.string.isRequired,
    nome: PropTypes.string.isRequired,
    preco_atual: PropTypes.number.isRequired,
    variacao_dia: PropTypes.number.isRequired,
    dividend_yield: PropTypes.number,
    searchedAt: PropTypes.string
  })).isRequired,
  onSelectFII: PropTypes.func.isRequired,
  selectedTicker: PropTypes.string,
  showRemoveButton: PropTypes.bool,
  onRemoveFII: PropTypes.func
}

export default FIIList

