import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { api, ApiError } from '../services/api.js'
import CategoryBadge from '../components/CategoryBadge.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'

function FlowerDetail() {
  const { id } = useParams()
  const [flower, setFlower] = useState(null)
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let cancelled = false
    setStatus('loading')
    api
      .getFlower(id)
      .then((data) => {
        if (cancelled) return
        setFlower(data)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          setStatus('not-found')
        } else {
          setErrorMessage(err instanceof ApiError ? err.message : 'Failed to load this flower.')
          setStatus('error')
        }
      })
    return () => {
      cancelled = true
    }
  }, [id])

  if (status === 'loading') return <LoadingState label="Loading flower…" />
  if (status === 'error') return <ErrorState message={errorMessage} />
  if (status === 'not-found') {
    return (
      <div>
        <p className="text-gray-700">No flower found with that id.</p>
        <Link to="/flowers" className="mt-2 inline-block text-emerald-700 hover:underline">Back to Explore</Link>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <Link to="/flowers" className="text-sm text-emerald-700 hover:underline">&larr; Back to Explore</Link>

      <div className="mt-3 flex items-start justify-between gap-3">
        <h1 className="text-3xl font-semibold text-gray-900">{flower.flower}</h1>
        <CategoryBadge category={flower.communication_category} />
      </div>

      <section className="mt-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Historical meaning</h2>
        <p className="mt-1 text-gray-800">{flower.historical_meaning}</p>
      </section>

      <section className="mt-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Human-language meaning</h2>
        <p className="mt-1 text-gray-800">{flower.human_language_meaning}</p>
      </section>

      <section className="mt-6 rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
        This is the project's supplied seed dataset. No source citation is
        recorded for this record yet — see{' '}
        <Link to="/about" className="text-emerald-700 hover:underline">About</Link>{' '}
        for how provenance will be added.
      </section>
    </div>
  )
}

export default FlowerDetail
