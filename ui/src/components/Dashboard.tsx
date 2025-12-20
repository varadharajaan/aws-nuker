import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface Stats {
  total_resources: number
  total_cost: number
  resources_by_service: Record<string, number>
  resources_by_region: Record<string, number>
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/api/stats`)
      setStats(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch statistics. Make sure the API server is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded">
        <p className="font-bold">Error</p>
        <p>{error}</p>
        <button
          onClick={fetchStats}
          className="mt-2 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Resources"
          value={stats?.total_resources || 0}
          icon="📦"
        />
        <StatCard
          title="Total Cost"
          value={`$${(stats?.total_cost || 0).toFixed(2)}`}
          icon="💰"
        />
        <StatCard
          title="Services"
          value={Object.keys(stats?.resources_by_service || {}).length}
          icon="🔧"
        />
        <StatCard
          title="Regions"
          value={Object.keys(stats?.resources_by_region || {}).length}
          icon="🌍"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Resources by Service</h2>
          <div className="space-y-2">
            {stats && Object.entries(stats.resources_by_service).map(([service, count]) => (
              <div key={service} className="flex justify-between items-center">
                <span className="font-medium">{service}</span>
                <span className="text-muted-foreground">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Resources by Region</h2>
          <div className="space-y-2">
            {stats && Object.entries(stats.resources_by_region).map(([region, count]) => (
              <div key={region} className="flex justify-between items-center">
                <span className="font-medium">{region}</span>
                <span className="text-muted-foreground">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionButton
            title="Discover Resources"
            description="Find resources across all regions"
            icon="🔍"
            href="#discover"
          />
          <ActionButton
            title="Run Dry-Run"
            description="Simulate cleanup without deleting"
            icon="🧪"
            href="#dryrun"
          />
          <ActionButton
            title="View Reports"
            description="Check audit logs and history"
            icon="📊"
            href="#reports"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon }: { title: string; value: string | number; icon: string }) {
  return (
    <div className="bg-card border rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}

function ActionButton({ title, description, icon, href }: {
  title: string
  description: string
  icon: string
  href: string
}) {
  return (
    <a
      href={href}
      className="block bg-secondary hover:bg-secondary/80 rounded-lg p-4 transition-colors"
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="text-sm text-muted-foreground">{description}</p>
    </a>
  )
}
