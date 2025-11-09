import { useState } from 'react'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-background text-foreground">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold">AWS Nuker Dashboard</h1>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <Dashboard />
        </main>
      </div>
    </div>
  )
}

export default App
