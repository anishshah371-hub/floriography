function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-3 py-10 text-gray-500" role="status" aria-live="polite">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-emerald-700" />
      <span>{label}</span>
    </div>
  )
}

export default LoadingState
