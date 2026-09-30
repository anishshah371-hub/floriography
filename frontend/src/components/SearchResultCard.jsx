import { useState } from 'react'
import { Link } from 'react-router'
import CategoryBadge from './CategoryBadge.jsx'

function SearchResultCard({ result }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <Link to={`/flowers/${result.id}`} className="font-medium text-gray-900 hover:text-emerald-700">
            {result.flower}
          </Link>
          <div className="mt-1"><CategoryBadge category={result.communication_category} /></div>
        </div>
        <span
          className="shrink-0 rounded bg-gray-100 px-2 py-1 text-xs font-mono text-gray-600"
          title="TF-IDF cosine similarity score"
        >
          {result.similarity_score.toFixed(3)}
        </span>
      </div>

      <p className="mt-3 text-sm text-gray-700">{result.human_language_meaning}</p>
      <p className="mt-1 text-xs text-gray-500">Historical meaning: {result.historical_meaning}</p>

      <button
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 text-sm font-medium text-emerald-700 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 rounded"
        aria-expanded={expanded}
      >
        {expanded ? 'Hide why this matched' : 'Why this matched'}
      </button>

      {expanded && (
        <div className="mt-2 rounded bg-gray-50 p-3 text-sm text-gray-700">
          <p>{result.explanation}</p>
          {result.matched_terms.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {result.matched_terms.map((term) => (
                <span key={term} className="rounded bg-white px-1.5 py-0.5 text-xs font-mono text-gray-600 ring-1 ring-gray-200">
                  {term}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SearchResultCard
