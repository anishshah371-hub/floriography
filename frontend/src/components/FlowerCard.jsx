import { Link } from 'react-router'
import CategoryBadge from './CategoryBadge.jsx'

function FlowerCard({ flower }) {
  return (
    <Link
      to={`/flowers/${flower.id}`}
      className="block rounded-lg border border-gray-200 p-4 transition hover:border-emerald-300 hover:shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-gray-900">{flower.flower}</h3>
        <CategoryBadge category={flower.communication_category} />
      </div>
      <p className="mt-1 text-sm text-gray-600">{flower.historical_meaning}</p>
    </Link>
  )
}

export default FlowerCard
