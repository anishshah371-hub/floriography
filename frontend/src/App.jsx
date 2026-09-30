import { Routes, Route, Link, NavLink } from 'react-router'
import Home from './pages/Home.jsx'
import FlowerExplorer from './pages/FlowerExplorer.jsx'
import FlowerDetail from './pages/FlowerDetail.jsx'
import SearchResults from './pages/SearchResults.jsx'
import Analytics from './pages/Analytics.jsx'
import About from './pages/About.jsx'

const NAV_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/flowers', label: 'Explore' },
  { to: '/search', label: 'Meaning Search' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/about', label: 'About' },
]

function App() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <nav className="border-b border-gray-200 px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <Link to="/" className="font-semibold text-emerald-800">Floriography</Link>
          <ul className="flex flex-wrap gap-5 text-sm font-medium">
            {NAV_LINKS.map((link) => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  end={link.end}
                  className={({ isActive }) => (isActive ? 'text-emerald-700' : 'text-gray-600 hover:text-emerald-700')}
                >
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </nav>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/flowers" element={<FlowerExplorer />} />
          <Route path="/flowers/:id" element={<FlowerDetail />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
