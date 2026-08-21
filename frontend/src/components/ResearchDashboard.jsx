import { useState, useEffect, useRef } from 'react'
import { getResearch } from '../api/index.js'

export default function ResearchDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const chartRefs = {
    accuracy: useRef(null),
    learning: useRef(null)
  }

  useEffect(() => {
    getResearch()
      .then(d => {
        setData(d)
        setLoading(false)
      })
      .catch(err => {
        setError("Failed to load research data.")
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (!data || !window.Chart) return

    const Chart = window.Chart
    
    // 1. Accuracy Comparison (Bar)
    if (data.model_comparison) {
      const accCtx = chartRefs.accuracy.current.getContext('2d')
      accChart = new Chart(accCtx, {
        type: 'bar',
        data: {
          labels: data.model_comparison.map(m => m.model),
          datasets: [{
            label: 'Accuracy %',
            data: data.model_comparison.map(m => m.accuracy),
            backgroundColor: data.model_comparison.map(m => m.model.includes('Current') ? '#10b981' : '#9ca3af'),
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { x: { min: 80, max: 100 } }
        }
      })
    }

    // 2. Learning Curves (Line)
    if (data.training_curves) {
      const learnCtx = chartRefs.learning.current.getContext('2d')
      learnChart = new Chart(learnCtx, {
        type: 'line',
        data: {
          labels: data.training_curves.epochs,
          datasets: [
            {
              label: 'Train Acc',
              data: data.training_curves.train_acc,
              borderColor: '#10b981',
              tension: 0.3,
              borderWidth: 3
            },
            {
              label: 'Val Acc',
              data: data.training_curves.val_acc,
              borderColor: '#3b82f6',
              tension: 0.3,
              borderDash: [5, 5]
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
          scales: { y: { min: 0.5, max: 1.0 } }
        }
      })
    }

    return () => {
      if (accChart) accChart.destroy()
      if (learnChart) learnChart.destroy()
    }
  }, [data])

  if (loading) return <div className="card" style={{ padding: '40px', textAlign: 'center' }}><span className="spinner spinner-green" /> Loading Research Metrics...</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-6)' }}>
      {/* Header Info */}
      <div className="card" style={{ padding: 'var(--sp-6)', background: 'linear-gradient(135deg, var(--green-900), var(--green-800))', color: '#fff' }}>
        <h3 style={{ marginBottom: 'var(--sp-2)' }}>Comparative AI Research</h3>
        <p style={{ fontSize: '.9rem', opacity: 0.9 }}>
          Evaluating 10-layer AI architecture performance across different model backends and training strategies.
        </p>
      </div>

      {/* Comparison Table */}
      <div className="card" style={{ padding: 'var(--sp-6)', overflowX: 'auto' }}>
        <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Performance Matrix</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.85rem' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--gray-100)' }}>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Architecture</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Accuracy</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>F1-Score</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Latence</th>
              <th style={{ padding: '12px 8px', color: 'var(--gray-500)' }}>Size</th>
            </tr>
          </thead>
          <tbody>
            {data.model_comparison.map((m, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--gray-50)', background: m.model.includes('Current') ? 'var(--green-50)' : 'transparent' }}>
                <td style={{ padding: '12px 8px', fontWeight: 600 }}>{m.model}</td>
                <td style={{ padding: '12px 8px' }}>{m.accuracy}%</td>
                <td style={{ padding: '12px 8px' }}>{m.f1_score}</td>
                <td style={{ padding: '12px 8px' }}>{m.inference_time_ms}ms</td>
                <td style={{ padding: '12px 8px' }}>{m.size_mb}MB</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--sp-6)' }}>
        <div className="card" style={{ padding: 'var(--sp-6)' }}>
          <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Accuracy Comparison</h4>
          <div style={{ height: 250 }}><canvas ref={chartRefs.accuracy}></canvas></div>
        </div>
        <div className="card" style={{ padding: 'var(--sp-6)' }}>
          <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Model Training Curve</h4>
          <div style={{ height: 250 }}><canvas ref={chartRefs.learning}></canvas></div>
        </div>
      </div>

      {/* Insights */}
      <div className="card" style={{ padding: 'var(--sp-6)' }}>
        <h4 style={{ marginBottom: 'var(--sp-4)', fontSize: '.9rem', color: 'var(--gray-600)' }}>Research Insights</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
          {data.insights.map((insight, i) => (
            <div key={i} style={{ display: 'flex', gap: 'var(--sp-3)', alignItems: 'start' }}>
              <span style={{ color: 'var(--green-600)', fontSize: '1.1rem' }}>✓</span>
              <p style={{ fontSize: '.9rem', color: 'var(--gray-600)', lineHeight: 1.5 }}>{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
