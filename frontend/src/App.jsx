import { useState } from 'react'
import './App.css'
import FIIList from './components/FIIList'
import TabNavigation from './components/TabNavigation'
import FIIDetail from './components/FIIDetail'
import CotacoesTab from './components/CotacoesTab'
import DividendosTab from './components/DividendosTab'
import PainelGeralTab from './components/PainelGeralTab'
import SearchBar from './components/SearchBar'
import { useFIIHistory } from './hooks/useFIIHistory'

function App() {
  // Hook de histórico de FIIs pesquisados
  const { history, addToHistory, clearHistory, removeFromHistory } = useFIIHistory()
  
  const [selectedFII, setSelectedFII] = useState(null)
  const [selectedTicker, setSelectedTicker] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('painel')
  const [sidebarVisible, setSidebarVisible] = useState(true) // Agora começa visível
  const [ultimaAtualizacao, setUltimaAtualizacao] = useState(null)

  const tabs = [
    { id: 'painel', label: 'Painel Geral', icon: '🎯' },
    { id: 'resumo', label: 'Resumo', icon: '📊' },
    { id: 'cotacoes', label: 'Cotações', icon: '📈' },
    { id: 'dividendos', label: 'Dividendos', icon: '💰' }
  ]

  const handleSearch = async (query) => {
    if (!query.trim()) {
      // Limpar seleção e voltar ao painel
      setSelectedTicker(null)
      setSelectedFII(null)
      setActiveTab('painel')
      setError(null)
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Busca se o FII existe
      const searchResponse = await fetch(`http://localhost:5001/api/search?q=${query}`)
      const searchData = await searchResponse.json()
      
      if (!searchResponse.ok) {
        throw new Error(searchData.erro || `FII ${query.toUpperCase()} não encontrado ou sem dados disponíveis no Yahoo Finance`)
      }
      
      if (searchData.existe) {
        const ticker = searchData.ticker
        
        // Busca detalhes do FII para mostrar na lista
        const detailsResponse = await fetch(`http://localhost:5001/api/fii/${ticker}`)
        
        if (detailsResponse.ok) {
          const detailsData = await detailsResponse.json()
          
          // Adiciona ao histórico (ou atualiza se já existe)
          addToHistory(detailsData)
          
          // Seleciona o FII
          setSelectedTicker(ticker.replace('.SA', ''))
          setSelectedFII(detailsData)
          setActiveTab('resumo')
          
          // Mostra sidebar se estava oculta
          setSidebarVisible(true)
          
          // Atualiza timestamp
          setUltimaAtualizacao(new Date().toISOString())
        }
      }
    } catch (err) {
      setError(err.message)
      setSelectedTicker(null)
      setSelectedFII(null)
    } finally {
      setLoading(false)
    }
  }
  
  const formatarDataAtualizacao = (isoDate) => {
    if (!isoDate) return 'Nunca'
    
    const data = new Date(isoDate)
    const agora = new Date()
    const diffMs = agora - data
    const diffMinutos = Math.floor(diffMs / 60000)
    
    if (diffMinutos < 1) return 'Agora mesmo'
    if (diffMinutos === 1) return 'Há 1 minuto'
    if (diffMinutos < 60) return `Há ${diffMinutos} minutos`
    
    const diffHoras = Math.floor(diffMinutos / 60)
    if (diffHoras === 1) return 'Há 1 hora'
    if (diffHoras < 24) return `Há ${diffHoras} horas`
    
    return data.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleSelectFII = (ticker) => {
    // Busca o FII no histórico
    const fiiData = history.find(f => f.ticker.replace('.SA', '') === ticker)
    
    if (fiiData) {
      setSelectedTicker(ticker)
      setSelectedFII(fiiData)
      
      if (activeTab === 'painel') {
        setActiveTab('resumo')
      }
    }
  }
  
  const handleRemoveFII = (ticker, e) => {
    // Evita propagar o clique para o card
    e.stopPropagation()
    
    removeFromHistory(ticker)
    
    // Se era o FII selecionado, limpa a seleção
    if (selectedTicker === ticker.replace('.SA', '')) {
      setSelectedTicker(null)
      setSelectedFII(null)
      setActiveTab('painel')
    }
  }
  
  const handleClearHistory = () => {
    if (confirm('Deseja limpar todo o histórico de FIIs pesquisados?')) {
      clearHistory()
      setSelectedTicker(null)
      setSelectedFII(null)
      setActiveTab('painel')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>📊 Monitor de FIIs</h1>
            <div className="header-glow"></div>
          </div>
          <p className="header-subtitle">Acompanhamento de Fundos Imobiliários em Tempo Real</p>
        </div>
      </header>

      <main className="app-main">
        <div className="search-section">
          <SearchBar onSearch={handleSearch} />
          
          {ultimaAtualizacao && (
            <div className="last-update-badge">
              <span className="update-icon">🕐</span>
              <span className="update-text">
                Última atualização: <strong>{formatarDataAtualizacao(ultimaAtualizacao)}</strong>
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <div className="error-content">
              <strong>Erro ao Buscar FII</strong>
              <p>{error}</p>
              <p className="error-hint">💡 Tente buscar outro FII. Exemplos: HGLG11, MXRF11, KNRI11</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-center">
            <div className="loading-spinner"></div>
            <p>Buscando FII...</p>
          </div>
        )}

        <div className={`content-grid ${!sidebarVisible ? 'sidebar-hidden' : ''}`}>
          {/* Sidebar - Mostra histórico de FIIs pesquisados */}
          {sidebarVisible && (
            <div className="fii-sidebar">
              <div className="sidebar-header">
                <h2>
                  <span className="sidebar-icon"></span>
                  FIIs Pesquisados
                  {history.length > 0 && (
                    <span className="history-count">{history.length}</span>
                  )}
                </h2>
                <div className="sidebar-actions">
                  {history.length > 0 && (
                    <button 
                      className="clear-history-btn"
                      onClick={handleClearHistory}
                      title="Limpar histórico"
                    >
                      🗑️
                    </button>
                  )}
                  <button 
                    className="toggle-sidebar-btn"
                    onClick={() => setSidebarVisible(false)}
                    title="Ocultar barra lateral"
                  >
                    ◀
                  </button>
                </div>
              </div>
              {history.length > 0 ? (
                <>
                  <div className="history-hint">
                    <span className="hint-icon">💡</span>
                    <span>Clique para navegar entre os FIIs</span>
                  </div>
                  <div className="fii-list-wrapper">
                    <FIIList 
                      fiis={history} 
                      onSelectFII={handleSelectFII}
                      onRemoveFII={handleRemoveFII}
                      selectedTicker={selectedTicker}
                      showRemoveButton={true}
                    />
                  </div>
                </>
              ) : (
                <div className="sidebar-empty">
                  <div className="empty-icon">🔍</div>
                  <p>Nenhum FII pesquisado ainda</p>
                  <p className="sidebar-suggestion-label">Experimente pesquisar:</p>
                  <div className="example-tickers">
                    <button 
                      className="ticker-suggestion"
                      onClick={() => handleSearch('HGLG11')}
                      title="Buscar HGLG11"
                    >
                      HGLG11
                    </button>
                    <button 
                      className="ticker-suggestion"
                      onClick={() => handleSearch('MXRF11')}
                      title="Buscar MXRF11"
                    >
                      MXRF11
                    </button>
                    <button 
                      className="ticker-suggestion"
                      onClick={() => handleSearch('KNRI11')}
                      title="Buscar KNRI11"
                    >
                      KNRI11
                    </button>
                  </div>
                  <p className="sidebar-tip">
                    💡 Os FIIs pesquisados ficarão salvos aqui para navegação rápida
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Botão para mostrar sidebar quando oculta */}
          {!sidebarVisible && (
            <button 
              className="show-sidebar-btn"
              onClick={() => setSidebarVisible(true)}
              title="Mostrar barra lateral"
            >
              ▶
            </button>
          )}

          {/* Main Content */}
          <div className="fii-content">
            <TabNavigation 
              tabs={tabs}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />

            <div className="tab-content">
              {activeTab === 'painel' && (
                <PainelGeralTab />
              )}

              {activeTab === 'resumo' && (
                selectedTicker && selectedFII ? (
                  <FIIDetail fii={selectedFII} />
                ) : (
                  <div className="no-selection">
                    <div className="no-selection-icon">🔍</div>
                    <h3>Nenhum FII Selecionado</h3>
                    <p>Use a barra de busca acima para pesquisar um FII</p>
                  </div>
                )
              )}
              
              {activeTab === 'cotacoes' && (
                selectedTicker ? (
                  <CotacoesTab ticker={selectedTicker} />
                ) : (
                  <div className="no-selection">
                    <div className="no-selection-icon">📈</div>
                    <h3>Nenhum FII Selecionado</h3>
                    <p>Busque um FII para visualizar cotações</p>
                  </div>
                )
              )}
              
              {activeTab === 'dividendos' && (
                selectedTicker ? (
                  <DividendosTab ticker={selectedTicker} />
                ) : (
                  <div className="no-selection">
                    <div className="no-selection-icon">💰</div>
                    <h3>Nenhum FII Selecionado</h3>
                    <p>Busque um FII para visualizar dividendos</p>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>📈 Dados fornecidos por Yahoo Finance</p>
          <p className="footer-tech">Desenvolvido com Python + Flask + React + Vite</p>
        </div>
      </footer>
    </div>
  )
}

export default App
