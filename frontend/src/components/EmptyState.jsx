function EmptyState({ title = 'Nothing here yet', hint }) {
  return (
    <div className="rounded-lg border border-dashed border-gray-300 px-4 py-10 text-center text-gray-500">
      <p className="font-medium">{title}</p>
      {hint && <p className="mt-1 text-sm">{hint}</p>}
    </div>
  )
}

export default EmptyState
