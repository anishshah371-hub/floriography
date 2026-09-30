import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, ApiError } from '../services/api.js'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'

function StatCard({ label, value }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4">
      <p className="text-2xl font-semibold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  )
}

function Analytics() {
  const [data, setData] = useState(null)
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    api
      .getAnalytics()
      .then((d) => {
        setData(d)
        setStatus('ready')
      })
      .catch((err) => {
        setErrorMessage(err instanceof ApiError ? err.message : 'Failed to load analytics.')
        setStatus('error')
      })
  }, [])

  if (status === 'loading') return <LoadingState label="Loading analytics…" />
  if (status === 'error') return <ErrorState message={errorMessage} />

  const chartData = Object.entries(data.category_distribution)
    .sort((a, b) => b[1] - a[1])
    .map(([category, count]) => ({ category, count }))

  return (
    <div>
      <h1 className="text-3xl font-semibold text-gray-900">Dataset Analytics</h1>
      <p className="mt-2 text-gray-600">
        Computed live from the database on every load — nothing on this page is hard-coded.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total flowers" value={data.total_records} />
        <StatCard label="Categories" value={data.category_count} />
        <StatCard label="Avg. historical meaning length" value={`${data.text_length_stats.historical_meaning.mean} chars`} />
        <StatCard label="Avg. human-language meaning length" value={`${data.text_length_stats.human_language_meaning.mean} chars`} />
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900">Flowers per category</h2>
        <div className="mt-3 h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} />
              <YAxis type="category" dataKey="category" width={120} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#047857" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {['historical_meaning', 'human_language_meaning'].map((field) => (
          <div key={field} className="rounded-lg border border-gray-200 p-4">
            <h3 className="font-medium text-gray-900">
              {field === 'historical_meaning' ? 'Historical meaning' : 'Human-language meaning'} length (characters)
            </h3>
            <dl className="mt-2 grid grid-cols-3 gap-2 text-sm">
              <div><dt className="text-gray-500">Min</dt><dd className="font-mono">{data.text_length_stats[field].min}</dd></div>
              <div><dt className="text-gray-500">Mean</dt><dd className="font-mono">{data.text_length_stats[field].mean}</dd></div>
              <div><dt className="text-gray-500">Max</dt><dd className="font-mono">{data.text_length_stats[field].max}</dd></div>
            </dl>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Analytics
