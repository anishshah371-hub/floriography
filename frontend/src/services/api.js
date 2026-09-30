// Thin fetch wrapper. Every component calls through here rather than
// hard-coding fetch()/URLs -- base URL comes from one env var so
// dev/prod/deploy never means hunting through components (spec
// section 35).
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, params = {}) {
  const url = new URL(BASE_URL + path)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value)
    }
  })

  let response
  try {
    response = await fetch(url)
  } catch {
    throw new ApiError('Could not reach the Floriography API. Is the backend running?', 0)
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON -- keep the generic message
    }
    throw new ApiError(detail, response.status)
  }

  return response.json()
}

export const api = {
  health: () => request('/api/health'),
  listFlowers: ({ search, category, limit = 20, offset = 0 } = {}) =>
    request('/api/flowers', { search, category, limit, offset }),
  getFlower: (id) => request(`/api/flowers/${id}`),
  searchFlowersByName: (query) => request('/api/flowers/search', { query }),
  listCategories: () => request('/api/flowers/categories'),
  searchMeaning: (query, { topK = 5, method = 'tfidf' } = {}) =>
    request('/api/search/meaning', { query, top_k: topK, method }),
  getAnalytics: () => request('/api/analytics'),
}

export { ApiError }
