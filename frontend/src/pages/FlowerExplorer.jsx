import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { api, ApiError } from '../services/api.js'
import FlowerCard from '../components/FlowerCard.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'

function FlowerExplorer() {
  const [searchParams, setSearchParams] = useSearchParams()
  const search = searchParams.get('search') || ''
  const category = searchParams.get('category') || ''

  const [categories, setCategories] = useState([])
  const [flowers, setFlowers] = useState([])
  const [total, setTotal] = useState(0)
  const [status, setStatus] = useState('loading') // loading | ready | error
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    api.listCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    api
      .listFlowers({ search, category, limit: 50 })
      .then((data) => {
        if (cancelled) return
        setFlowers(data.results)
        setTotal(data.total)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        setErrorMessage(err instanceof ApiError ? err.message : 'Failed to load flowers.')
        setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [search, category])

  function updateParam(key, val) {
    const next = new URLSearchParams(searchParams)
    if (val) next.set(key, val)
    else next.delete(key)
    setSearchParams(next)
  }

  return (
    <div>
      <h1 className="text-3xl font-semibold text-gray-900">Explore Flowers</h1>
      <p className="mt-2 text-gray-600">Browse the documented dataset — {total} flower{total === 1 ? '' : 's'}.</p>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="text"
          value={search}
          onChange={(e) => updateParam('search', e.target.value)}
          placeholder="Search by flower name…"
          className="flex-1 min-w-[200px] rounded-lg border border-gray-300 px-3 py-2 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
        />
        <select
          value={category}
          onChange={(e) => updateParam('category', e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div className="mt-6">
        {status === 'loading' && <LoadingState label="Loading flowers…" />}
        {status === 'error' && <ErrorState message={errorMessage} />}
        {status === 'ready' && flowers.length === 0 && (
          <EmptyState title="No flowers match" hint="Try a different name or clear the category filter." />
        )}
        {status === 'ready' && flowers.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {flowers.map((f) => (
              <FlowerCard key={f.id} flower={f} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default FlowerExplorer
