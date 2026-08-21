import { useState, useEffect, useRef } from 'react'
import { getAnalytics } from '../api/index.js'

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const chartRefs = {
    distribution: useRef(null),
    severity: useRef(null),
    trend: useRef(null)
  }

  useEffect(() => {
    getAnalytics()
      .then(d => {
        setData(d)
        setLoading(false)
      })
      .catch(err => {
        setError("Failed to load analytics data. Ensure backend is running.")
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (!data || !window.Chart) return

    const Chart = window.Chart
    
    // 1. Disease Distribution Chart (Doughnut)
    if (data.disease_distribution && Object.keys(data.disease_distribution).length > 0) {
      const distCtx = chartRefs.distribution.current.getContext('2d')
      distChart = new Chart(distCtx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(data.disease_distribution),
          datasets: [{
            data: Object.values(data.disease_distribution),
            backgroundColor: ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } } }
        }
      })
    }

    // 2. Severity Distribution Chart (Bar)
    if (data.severity_distribution && Object.keys(data.severity_distribution).length > 0) {
      const sevCtx = chartRefs.severity.current.getContext('2d')
      sevChart = new Chart(sevCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(data.severity_distribution),
          datasets: [{
            label: 'Total Scans',
            data: Object.values(data.severity_distribution),
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6b7280', '#9ca3af'],
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, grid: { display: false } }, x: { grid: { display: false } } }
        }
      })
    }

    return () => {
      if (distChart) distChart.destroy()
      if (sevChart) sevChart.destroy()
    }
  }, [data])

  if (loading) return <div className="card" style={{ padding: '40px', textAlign: 'center' }}><span className="spinner spinner-green" /> Loading AI Analytics...</div>
  if (error) return <div className="alert alert-danger"><span>⚠️</span><span>{error}</span></div>
  if (data?.total_scans === 0) return (
    <div className="card" style={{ padding: '60px', textAlign: 'center' }}>
      <div style={{ fontSize: 50, marginBottom: 20 }}>📊</div>
      <h3 style={{ color: 'var(--gray-700)' }}>No Prediction Data Yet</h3>
      <p style={{ color: 'var(--gray-500)' }}>Start scanning leaves to see real-time AI analytics and trends.</p>
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-6)' }}>
      {/* Top Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--sp-4)' }}>
        {[
          { label: 'Total Scans', value: data.total_scans, icon: '🔍', color: 'var(--green-600)' },
          { label: 'Avg Confidence', value: `${data.avg_confidence}%`, icon: '🎯', color: 'var(--blue-600)' },
          { label: 'Major Issue', value: Object.keys(data.disease_distribution)[0] || 'N/A', icon: '⚠️', color: 'var(--red-600)' },
        ].map(stat => (
          <div key={stat.label} className="card" style={{ padding: 'var(--sp-4)', display: 'flex', alignItems: 'center', gap: 'var(--sp-4)' }}>
            <div style={{ fontSize: 24, background: 'var(--gray-50)', width: 48, height: 48, borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{stat.icon}</div>
            <div>
              <p style={{ fontSize: '.75rem', color: 'var(--gray-500)', textTransform: 'uppercase' }}>{stat.label}</p>
              <p style={{ fontSize: '1.25rem', fontWeight: 700, color: stat.color }}>{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--sp-6)' }}>
        <div className="card" style={{ padding: 'var(--sp-6)' }}>
          <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Disease Distribution</h4>
          <div style={{ height: 250 }}><canvas ref={chartRefs.distribution}></canvas></div>
        </div>
        <div className="card" style={{ padding: 'var(--sp-6)' }}>
          <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Severity Breakdown</h4>
          <div style={{ height: 250 }}><canvas ref={chartRefs.severity}></canvas></div>
        </div>
      </div>

      {/* Recent History Table */}
      <div className="card" style={{ padding: 'var(--sp-6)', overflowX: 'auto' }}>
        <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Recent Prediction Log</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.85rem' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--gray-100)' }}>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Disease</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Confidence</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Severity</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {data.recent_activity.reverse().map((p, i) => (
              <tr key={i} style={{ borderBottom: i === data.recent_activity.length - 1 ? 'none' : '1px solid var(--gray-50)' }}>
                <td style={{ padding: '12px 8px', fontWeight: 600, color: 'var(--gray-800)' }}>{p.display_name}</td>
                <td style={{ padding: '12px 8px' }}><span className="badge badge-green">{p.confidence}%</span></td>
                <td style={{ padding: '12px 8px' }}>
                  <span className={`badge ${p.severity === 'Severe' ? 'badge-red' : p.severity === 'Moderate' ? 'badge-yellow' : 'badge-green'}`}>
                    {p.severity}
                  </span>
                </td>
                <td style={{ padding: '12px 8px', color: 'var(--gray-400)', fontSize: '.75rem' }}>
                  {new Date(p.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
