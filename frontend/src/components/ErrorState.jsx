function ErrorState({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-red-800" role="alert">
      <p>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 rounded border border-red-300 px-3 py-1 text-sm font-medium hover:bg-red-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
        >
          Try again
        </button>
      )}
    </div>
  )
}

export default ErrorState
