import { useState, useEffect } from 'react'
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react'
import {
  formatPercent,
  formatCurrency,
  CHART_COLORS
} from '../utils/chartUtils'
import './PainelGeralTab.css'

function PainelGeralTab() {
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [ultimaAtualizacao, setUltimaAtualizacao] = useState(null)
  const [analiseIA, setAnaliseIA] = useState(null)
  const [loadingIA, setLoadingIA] = useState(false)
  const [errorIA, setErrorIA] = useState(null)

  useEffect(() => {
    buscarPainelGeral()
  }, [])

  const buscarPainelGeral = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:5001/api/fiis')
      
      if (!response.ok) {
        throw new Error('Erro ao buscar dados do painel')
      }

      const data = await response.json()
      
      // Atualiza timestamp
      if (data.ultima_atualizacao) {
        setUltimaAtualizacao(data.ultima_atualizacao)
      }
      
      // Processa dados para o painel
      const fiis = data.fiis || data // Compatibilidade com formato antigo
      const processados = processarDados(fiis)
      setDados(processados)
      
      // Gera análise de IA automaticamente
      gerarAnaliseIA(processados)
    } catch (err) {
      setError(err.message)
      console.error('Erro:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const gerarAnaliseIA = async (dadosProcessados) => {
    if (!dadosProcessados) return
    
    setLoadingIA(true)
    setErrorIA(null)

    try {
      const response = await fetch('http://localhost:5001/api/analise-ia', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          maioresAltas: dadosProcessados.top5Altas,      // Envia Top 5 para IA
          maioresBaixas: dadosProcessados.top5Baixas,    // Envia Top 5 para IA
          maioresDescontos: dadosProcessados.maioresDescontos || [], // FIIs com desconto P/VP
          estatisticas: dadosProcessados.estatisticas
        })
      })
      
      if (!response.ok) {
        throw new Error('Erro ao gerar análise de IA')
      }

      const data = await response.json()
      setAnaliseIA(data)
    } catch (err) {
      setErrorIA(err.message)
      console.error('Erro IA:', err)
    } finally {
      setLoadingIA(false)
    }
  }

  const processarDados = (fiis) => {
    // Filtra FIIs válidos
    const validos = fiis.filter(f => f.preco_atual > 0)
    
    // Separa em altas e baixas
    const fiisEmAlta = validos.filter(f => f.variacao_dia > 0)
      .sort((a, b) => b.variacao_dia - a.variacao_dia)
      .map(f => ({
        ticker: f.ticker.replace('.SA', ''),
        nome: f.nome,
        preco: f.preco_atual,
        variacao: f.variacao_dia * 100,
        volume: f.volume,
        pvp: f.pvp,
        dy: f.dividend_yield
      }))
    
    const fiisEmBaixa = validos.filter(f => f.variacao_dia < 0)
      .sort((a, b) => a.variacao_dia - b.variacao_dia)
      .map(f => ({
        ticker: f.ticker.replace('.SA', ''),
        nome: f.nome,
        preco: f.preco_atual,
        variacao: f.variacao_dia * 100,
        volume: f.volume,
        pvp: f.pvp,
        dy: f.dividend_yield
      }))
    
    // Oportunidades P/VP: Menores P/VP entre os TOP 5 MAIORES BAIXAS
    // Analisa apenas os fundos que estão caindo mais forte
    const top5BaixasComPVP = fiisEmBaixa
      .slice(0, 5)  // Pega as TOP 5 maiores baixas
      .filter(f => f.pvp && f.pvp > 0)  // Filtra as que têm P/VP
    
    const comDesconto = top5BaixasComPVP
      .sort((a, b) => a.pvp - b.pvp)  // Ordena por menor P/VP
      .map(f => ({
        ticker: f.ticker,
        nome: f.nome,
        preco: f.preco,
        variacao: f.variacao,
        pvp: f.pvp,
        desconto: f.pvp < 1.0 ? ((1 - f.pvp) * 100) : 0,
        dy: f.dy,
        volume: f.volume,
        emBaixa: true
      }))
    
    // Top 5 para a IA analisar
    const top5Altas = fiisEmAlta.slice(0, 5)
    const top5Baixas = fiisEmBaixa.slice(0, 5)

    // Estatísticas gerais
    const totalFiis = validos.length
    const totalEmAlta = fiisEmAlta.length
    const totalEmBaixa = fiisEmBaixa.length
    const estaveis = validos.filter(f => f.variacao_dia === 0).length
    
    const variacaoMedia = validos.reduce((acc, f) => acc + f.variacao_dia, 0) / totalFiis * 100
    
    return {
      todosAltas: fiisEmAlta,        // TODOS os FIIs em alta
      todosBaixas: fiisEmBaixa,      // TODOS os FIIs em baixa
      top5Altas: top5Altas,          // Top 5 para IA
      top5Baixas: top5Baixas,        // Top 5 para IA
      maioresDescontos: comDesconto, // FIIs com P/VP < 1.0
      estatisticas: {
        total: totalFiis,
        emAlta: totalEmAlta,
        emBaixa: totalEmBaixa,
        estaveis,
        variacaoMedia
      }
    }
  }
  
  const formatarDataAtualizacao = (isoDate) => {
    if (!isoDate) return 'Nunca'
    
    const data = new Date(isoDate)
    return data.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="painel-geral-tab">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando painel geral...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="painel-geral-tab">
        <div className="error-container">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  if (!dados) {
    return (
      <div className="painel-geral-tab">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>Nenhum dado disponível</h3>
          <p>Não foi possível carregar informações dos FIIs</p>
        </div>
      </div>
    )
  }

  // Dados para treemap (usa Top 15 para melhor visualização)
  const treemapDataAltas = dados.todosAltas.slice(0, 15).map(f => ({
    name: f.ticker,
    size: Math.abs(f.variacao) * 100, // Usa valor absoluto multiplicado para ter números > 1
    variacao: f.variacao,
    preco: f.preco
  }))

  const treemapDataBaixas = dados.todosBaixas.slice(0, 15).map(f => ({
    name: f.ticker,
    size: Math.abs(f.variacao) * 100, // Usa valor absoluto
    variacao: f.variacao,
    preco: f.preco
  }))
  
  // Componente customizado para renderizar células do treemap com gradiente
  const CustomTreemapContent = (props) => {
    const { x, y, width, height, name, variacao, preco, index, data } = props
    
    // Não renderiza se muito pequeno
    if (width < 60 || height < 40) return null
    
    const isPositive = variacao >= 0
    
    // Calcula intensidade da cor baseado na posição (índice)
    // Primeiro item = cor mais intensa, último = cor mais clara
    const totalItems = data ? data.length : 15
    const position = index || 0
    const intensityFactor = 1 - (position / totalItems) * 0.5 // Varia de 1.0 a 0.5
    
    // Cores com gradiente de intensidade
    const getColor = () => {
      if (isPositive) {
        // Verde: do escuro (#059669) ao claro (#10b981)
        const r = Math.round(5 + (16 - 5) * (1 - intensityFactor))
        const g = Math.round(150 + (185 - 150) * (1 - intensityFactor))
        const b = Math.round(105 + (129 - 105) * (1 - intensityFactor))
        return `rgb(${r}, ${g}, ${b})`
      } else {
        // Vermelho: do escuro (#b91c1c) ao claro (#dc2626)
        const r = Math.round(185 + (220 - 185) * (1 - intensityFactor))
        const g = Math.round(28 + (38 - 28) * (1 - intensityFactor))
        const b = Math.round(28 + (38 - 28) * (1 - intensityFactor))
        return `rgb(${r}, ${g}, ${b})`
      }
    }
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: getColor(),
            stroke: '#0f172a',
            strokeWidth: 2.5,
            opacity: 0.95
          }}
        />
        {width > 80 && height > 50 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 8}
              textAnchor="middle"
              fill="white"
              stroke="none"
              fontSize="14"
              fontWeight="700"
              fontFamily="JetBrains Mono, monospace"
              paintOrder="stroke"
            >
              {name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 12}
              textAnchor="middle"
              fill="white"
              stroke="none"
              fontSize="16"
              fontWeight="800"
              fontFamily="JetBrains Mono, monospace"
              paintOrder="stroke"
            >
              {formatPercent(variacao)}
            </text>
          </>
        )}
        {width > 60 && width <= 80 && height > 40 && (
          <text
            x={x + width / 2}
            y={y + height / 2 + 4}
            textAnchor="middle"
            fill="white"
            stroke="none"
            fontSize="12"
            fontWeight="700"
            fontFamily="JetBrains Mono, monospace"
            paintOrder="stroke"
          >
            {name}
          </text>
        )}
      </g>
    )
  }

  return (
    <div className="painel-geral-tab">
      {/* Header */}
      <div className="painel-header">
        <div className="header-title-section">
          <h3 className="painel-title">
            <Activity size={28} />
            Painel Geral do Mercado
          </h3>
          <button onClick={buscarPainelGeral} className="refresh-button" disabled={loading}>
            <span className={`refresh-icon ${loading ? 'spinning' : ''}`}>🔄</span>
            Atualizar
          </button>
        </div>
        
        {ultimaAtualizacao && (
          <div className="painel-update-info">
            <span className="update-icon">🕐</span>
            <span className="update-text">
              Última atualização: <strong>{formatarDataAtualizacao(ultimaAtualizacao)}</strong>
            </span>
          </div>
        )}
      </div>

      {/* Análise de IA */}
      {analiseIA && (
        <div className="analise-ia-container">
          <div className="analise-ia-header">
            <h3>
              <span className="ia-icon">🤖</span>
              Análise de IA - Estratégia Antifrágil
            </h3>
            <span className="ia-badge">GPT-4</span>
          </div>
          <div className="analise-ia-content">
            {analiseIA.analise.split('\n').map((paragrafo, index) => {
              const linha = paragrafo.trim()
              if (!linha) return null
              
              // Converte markdown **texto** para <strong>texto</strong>
              let linhaFormatada = linha.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
              
              // Destaca tickers (padrão: letras maiúsculas terminadas em 11)
              // Mas não se já estiver dentro de <strong>
              linhaFormatada = linhaFormatada.replace(/(?<!<strong>)\b([A-Z]{4,6}11)\b(?![^<]*<\/strong>)/g, '<strong class="ticker">$1</strong>')
              
              return (
                <p key={index} dangerouslySetInnerHTML={{ __html: linhaFormatada }} />
              )
            })}
          </div>
          <div className="analise-ia-footer">
            <span className="ia-timestamp">
              🕐 Gerada {formatarDataAtualizacao(analiseIA.timestamp)}
            </span>
            <button 
              className="regenerate-btn"
              onClick={() => gerarAnaliseIA(dados)}
              disabled={loadingIA}
            >
              {loadingIA ? '⏳ Gerando...' : '🔄 Regenerar Análise'}
            </button>
          </div>
        </div>
      )}
      
      {loadingIA && !analiseIA && (
        <div className="analise-ia-loading">
          <div className="ia-spinner"></div>
          <p>🤖 Gerando análise antifrágil com IA...</p>
        </div>
      )}
      
      {errorIA && (
        <div className="analise-ia-error">
          <span className="error-icon">⚠️</span>
          <p>{errorIA}</p>
        </div>
      )}

      {/* Estatísticas Gerais */}
      <div className="estatisticas-mercado">
        <div className="stat-card total">
          <div className="stat-header">
            <BarChart3 size={20} />
            <span className="stat-label">Total de FIIs</span>
          </div>
          <span className="stat-value">{dados.estatisticas.total}</span>
        </div>

        <div className="stat-card alta">
          <div className="stat-header">
            <TrendingUp size={20} />
            <span className="stat-label">Em Alta</span>
          </div>
          <span className="stat-value">{dados.estatisticas.emAlta}</span>
          <span className="stat-percent">
            {((dados.estatisticas.emAlta / dados.estatisticas.total) * 100).toFixed(1)}%
          </span>
        </div>

        <div className="stat-card baixa">
          <div className="stat-header">
            <TrendingDown size={20} />
            <span className="stat-label">Em Baixa</span>
          </div>
          <span className="stat-value">{dados.estatisticas.emBaixa}</span>
          <span className="stat-percent">
            {((dados.estatisticas.emBaixa / dados.estatisticas.total) * 100).toFixed(1)}%
          </span>
        </div>

        <div className="stat-card media">
          <div className="stat-header">
            <Activity size={20} />
            <span className="stat-label">Variação Média</span>
          </div>
          <span className={`stat-value ${dados.estatisticas.variacaoMedia >= 0 ? 'positive' : 'negative'}`}>
            {formatPercent(dados.estatisticas.variacaoMedia)}
          </span>
        </div>
      </div>

      {/* Oportunidades P/VP (TOP 5 Maiores Baixas) */}
      {dados.maioresDescontos && dados.maioresDescontos.length > 0 && (
        <div className="secao-analise">
          <div className="secao-header desconto">
            <span style={{ fontSize: '24px' }}>💎</span>
            <h4>💰 Oportunidades P/VP - TOP 5 Maiores Baixas ({dados.maioresDescontos.length})</h4>
          </div>

          <div className="cards-grid">
            {dados.maioresDescontos.map((fii, index) => (
              <div key={fii.ticker} className="fii-opportunity-card desconto em-baixa">
                <div className="card-rank">#{index + 1}</div>
                <div className="badge-destaque">🔥 Em Baixa</div>
                <div className="card-content">
                  <h5 className="card-ticker">{fii.ticker}</h5>
                  <p className="card-nome">{fii.nome}</p>
                  <div className="card-metrics">
                    <div className="metric">
                      <span className="metric-label">P/VP</span>
                      <span className="metric-value pvp">{fii.pvp?.toFixed(2) || 'N/A'}</span>
                    </div>
                    {fii.desconto > 0 && (
                      <div className="metric highlight">
                        <span className="metric-label">Desconto</span>
                        <span className="metric-value desconto-value">
                          {fii.desconto?.toFixed(1)}%
                        </span>
                      </div>
                    )}
                    <div className="metric">
                      <span className="metric-label">Hoje</span>
                      <span className="metric-value negativo">
                        {fii.variacao?.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                  <div className="card-extra-info">
                    <span className="extra-item">
                      💰 DY: <strong>{fii.dy ? `${fii.dy.toFixed(2)}%` : 'N/A'}</strong>
                    </span>
                    <span className="extra-item">
                      📊 Vol: <strong>{fii.volume > 0 ? `${(fii.volume / 1000).toFixed(0)}K` : 'Baixo'}</strong>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Maiores Altas */}
      <div className="secao-analise">
        <div className="secao-header alta">
          <TrendingUp size={24} />
          <h4>🚀 FIIs em Alta ({dados.todosAltas.length})</h4>
        </div>

        <div className="cards-grid">
          {dados.todosAltas.map((fii, index) => (
            <div key={fii.ticker} className="fii-opportunity-card alta">
              <div className="card-rank">#{index + 1}</div>
              <div className="card-content">
                <h5 className="card-ticker">{fii.ticker}</h5>
                <p className="card-nome">{fii.nome}</p>
                <div className="card-metrics">
                  <div className="metric">
                    <span className="metric-label">Preço</span>
                    <span className="metric-value">{formatCurrency(fii.preco)}</span>
                  </div>
                  <div className="metric highlight">
                    <span className="metric-label">Variação</span>
                    <span className="metric-value positive">
                      ▲ {formatPercent(fii.variacao)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Treemap Altas */}
        <div className="chart-container treemap-container">
          <h4 className="treemap-title">Visualização por Intensidade de Alta</h4>
          <ResponsiveContainer width="100%" height={400}>
            <Treemap
              data={treemapDataAltas}
              dataKey="size"
              stroke="#1e293b"
              strokeWidth={2}
              content={<CustomTreemapContent />}
            >
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div style={{
                        background: 'rgba(30, 41, 59, 0.95)',
                        border: '1px solid rgba(71, 85, 105, 0.8)',
                        borderRadius: '12px',
                        padding: '12px 16px',
                        backdropFilter: 'blur(10px)'
                      }}>
                        <p style={{ 
                          color: '#cbd5e1', 
                          fontWeight: '700', 
                          margin: '0 0 8px 0',
                          fontFamily: 'JetBrains Mono, monospace',
                          fontSize: '14px'
                        }}>
                          {data.name}
                        </p>
                        <p style={{ 
                          color: CHART_COLORS.bull, 
                          fontWeight: '800', 
                          margin: '0',
                          fontFamily: 'JetBrains Mono, monospace',
                          fontSize: '16px'
                        }}>
                          {formatPercent(data.variacao)}
                        </p>
                        <p style={{ 
                          color: '#94a3b8', 
                          fontSize: '12px',
                          margin: '4px 0 0 0'
                        }}>
                          {formatCurrency(data.preco)}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
            </Treemap>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Maiores Baixas */}
      <div className="secao-analise">
        <div className="secao-header baixa">
          <TrendingDown size={24} />
          <h4>💎 FIIs em Baixa ({dados.todosBaixas.length})</h4>
        </div>

        <div className="cards-grid">
          {dados.todosBaixas.map((fii, index) => (
            <div key={fii.ticker} className="fii-opportunity-card baixa">
              <div className="card-rank">#{index + 1}</div>
              <div className="card-content">
                <h5 className="card-ticker">{fii.ticker}</h5>
                <p className="card-nome">{fii.nome}</p>
                <div className="card-metrics">
                  <div className="metric">
                    <span className="metric-label">Preço</span>
                    <span className="metric-value">{formatCurrency(fii.preco)}</span>
                  </div>
                  <div className="metric highlight">
                    <span className="metric-label">Variação</span>
                    <span className="metric-value negative">
                      ▼ {formatPercent(fii.variacao)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Treemap Baixas */}
        <div className="chart-container treemap-container">
          <h4 className="treemap-title">Visualização por Intensidade de Queda</h4>
          <ResponsiveContainer width="100%" height={400}>
            <Treemap
              data={treemapDataBaixas}
              dataKey="size"
              stroke="#1e293b"
              strokeWidth={2}
              content={<CustomTreemapContent />}
            >
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div style={{
                        background: 'rgba(30, 41, 59, 0.95)',
                        border: '1px solid rgba(71, 85, 105, 0.8)',
                        borderRadius: '12px',
                        padding: '12px 16px',
                        backdropFilter: 'blur(10px)'
                      }}>
                        <p style={{ 
                          color: '#cbd5e1', 
                          fontWeight: '700', 
                          margin: '0 0 8px 0',
                          fontFamily: 'JetBrains Mono, monospace',
                          fontSize: '14px'
                        }}>
                          {data.name}
                        </p>
                        <p style={{ 
                          color: CHART_COLORS.bear, 
                          fontWeight: '800', 
                          margin: '0',
                          fontFamily: 'JetBrains Mono, monospace',
                          fontSize: '16px'
                        }}>
                          {formatPercent(data.variacao)}
                        </p>
                        <p style={{ 
                          color: '#94a3b8', 
                          fontSize: '12px',
                          margin: '4px 0 0 0'
                        }}>
                          {formatCurrency(data.preco)}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
            </Treemap>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default PainelGeralTab

