import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { api, ApiError } from '../services/api.js'
import SearchResultCard from '../components/SearchResultCard.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'

function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('query') || ''
  const [inputValue, setInputValue] = useState(query)

  const [response, setResponse] = useState(null)
  const [status, setStatus] = useState(query ? 'loading' : 'idle')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    setInputValue(query)
    if (!query) {
      setStatus('idle')
      return
    }
    let cancelled = false
    setStatus('loading')
    api
      .searchMeaning(query)
      .then((data) => {
        if (cancelled) return
        setResponse(data)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        setErrorMessage(err instanceof ApiError ? err.message : 'Search failed.')
        setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [query])

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (trimmed) setSearchParams({ query: trimmed })
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold text-gray-900">Meaning Search</h1>
      <p className="mt-2 text-gray-600">Describe what you want to communicate.</p>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder='e.g. "I want to express gratitude"'
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
        />
        <button
          type="submit"
          className="rounded-lg bg-emerald-700 px-5 py-2.5 font-medium text-white hover:bg-emerald-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
        >
          Search
        </button>
      </form>

      <div className="mt-6 space-y-3">
        {status === 'idle' && (
          <EmptyState title="Describe a feeling or intention above" hint='Try "I want to say goodbye" or "friendship".' />
        )}
        {status === 'loading' && <LoadingState label="Searching…" />}
        {status === 'error' && <ErrorState message={errorMessage} />}
        {status === 'ready' && response.results.length === 0 && (
          <EmptyState title="No strong documented matches were found" hint="Try a broader phrase, or search for a flower directly." />
        )}
        {status === 'ready' &&
          response.results.map((result) => <SearchResultCard key={result.id} result={result} />)}
      </div>
    </div>
  )
}

export default SearchResults
