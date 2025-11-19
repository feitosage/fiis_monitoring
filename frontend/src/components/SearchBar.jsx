import { useState } from 'react'
import PropTypes from 'prop-types'
import './SearchBar.css'

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  return (
    <div className="search-bar-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Digite o código do FII (ex: HGLG11, MXRF11, KNRI11)"
          value={query}
          onChange={(e) => setQuery(e.target.value.toUpperCase())}
          onKeyPress={handleKeyPress}
          className="search-input"
          maxLength={10}
        />
        <span className="search-icon">🔍</span>
      </div>
      <div className="search-hint">
        <span className="search-hint-icon">💡</span>
        <span>Pressione Enter para buscar ou navegue pela lista abaixo</span>
      </div>
    </div>
  )
}

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired
}

export default SearchBar
