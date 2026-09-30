import { useState } from 'react'
import { useNavigate } from 'react-router'

function Home() {
  const [mode, setMode] = useState('meaning') // 'flower' | 'meaning'
  const [value, setValue] = useState('')
  const navigate = useNavigate()

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) return
    if (mode === 'flower') {
      navigate(`/flowers?search=${encodeURIComponent(trimmed)}`)
    } else {
      navigate(`/search?query=${encodeURIComponent(trimmed)}`)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-3xl font-semibold text-gray-900">Floriography</h1>
      <p className="mt-2 text-gray-600">
        The documented symbolic language of flowers. Search for a flower to see
        its meaning, or describe what you want to communicate to find flowers
        whose documented symbolism matches.
      </p>

      <div className="mt-8 flex rounded-lg border border-gray-200 p-1 text-sm font-medium">
        <button
          onClick={() => setMode('meaning')}
          className={`flex-1 rounded-md px-3 py-2 transition ${mode === 'meaning' ? 'bg-emerald-700 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
        >
          Meaning → Flower
        </button>
        <button
          onClick={() => setMode('flower')}
          className={`flex-1 rounded-md px-3 py-2 transition ${mode === 'flower' ? 'bg-emerald-700 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
        >
          Flower → Meaning
        </button>
      </div>

      <form onSubmit={handleSubmit} className="mt-4">
        <label htmlFor="home-search" className="sr-only">
          {mode === 'meaning' ? 'What do you want to communicate?' : 'Search for a flower'}
        </label>
        <div className="flex gap-2">
          <input
            id="home-search"
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={mode === 'meaning' ? 'e.g. "I want to express gratitude"' : 'e.g. "Rose" or "Rose, Red"'}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600"
          />
          <button
            type="submit"
            className="rounded-lg bg-emerald-700 px-5 py-2.5 font-medium text-white hover:bg-emerald-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
          >
            Search
          </button>
        </div>
      </form>

      <p className="mt-3 text-sm text-gray-500">
        {mode === 'meaning'
          ? 'Results are retrieved from a documented dataset (TF-IDF + cosine similarity), not generated.'
          : `Try "rose", "lily", or any flower name.`}
      </p>
    </div>
  )
}

export default Home
