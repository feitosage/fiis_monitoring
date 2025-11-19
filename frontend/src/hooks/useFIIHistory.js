import { useState, useEffect } from 'react'

const STORAGE_KEY = 'fii_history'
const MAX_HISTORY_SIZE = 10

/**
 * Hook customizado para gerenciar histórico de FIIs pesquisados
 * Mantém cache em localStorage para persistência entre sessões
 */
export function useFIIHistory() {
  const [history, setHistory] = useState(() => {
    // Carrega histórico do localStorage ao inicializar
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch (error) {
      console.error('Erro ao carregar histórico:', error)
      return []
    }
  })

  // Salva no localStorage sempre que o histórico mudar
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    } catch (error) {
      console.error('Erro ao salvar histórico:', error)
    }
  }, [history])

  /**
   * Adiciona um FII ao histórico
   * Se já existe, move para o topo e atualiza timestamp
   */
  const addToHistory = (fiiData) => {
    setHistory((prev) => {
      // Remove se já existir
      const filtered = prev.filter(item => item.ticker !== fiiData.ticker)
      
      // Adiciona no início com timestamp
      const newItem = {
        ...fiiData,
        searchedAt: new Date().toISOString()
      }
      
      const updated = [newItem, ...filtered]
      
      // Limita ao tamanho máximo
      return updated.slice(0, MAX_HISTORY_SIZE)
    })
  }

  /**
   * Remove um FII específico do histórico
   */
  const removeFromHistory = (ticker) => {
    setHistory((prev) => prev.filter(item => item.ticker !== ticker))
  }

  /**
   * Limpa todo o histórico
   */
  const clearHistory = () => {
    setHistory([])
  }

  /**
   * Busca um FII específico no histórico
   */
  const getFromHistory = (ticker) => {
    return history.find(item => item.ticker === ticker)
  }

  /**
   * Verifica se um FII está no histórico
   */
  const isInHistory = (ticker) => {
    return history.some(item => item.ticker === ticker)
  }

  /**
   * Atualiza dados de um FII no histórico
   */
  const updateInHistory = (ticker, updatedData) => {
    setHistory((prev) => 
      prev.map(item => 
        item.ticker === ticker 
          ? { ...item, ...updatedData, updatedAt: new Date().toISOString() }
          : item
      )
    )
  }

  return {
    history,
    addToHistory,
    removeFromHistory,
    clearHistory,
    getFromHistory,
    isInHistory,
    updateInHistory,
    historySize: history.length
  }
}

