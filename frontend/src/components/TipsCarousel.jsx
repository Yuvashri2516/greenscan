// src/components/TipsCarousel.jsx
import { useState, useEffect } from 'react'
import { getFarmingTips } from '../api/index.js'

const FALLBACK_TIPS = [
  { id:1, icon:'🌱', category:'Crop Care', title:'Morning Watering is Best', body:'Water your plants early morning so leaves dry during the day. Wet foliage overnight encourages fungal diseases.' },
  { id:2, icon:'🪱', category:'Soil Health', title:'Add Compost Monthly', body:'Incorporate organic compost every 4–6 weeks. It improves water retention, drainage, and provides slow-release nutrients.' },
  { id:3, icon:'🛡️', category:'Prevention', title:'Crop Rotation Saves Crops', body:'Never plant tomatoes in the same spot 2 years in a row. Rotate with legumes to break disease cycles naturally.' },
  { id:4, icon:'☀️', category:'Seasonal', title:'Summer Heat Stress', body:'During peak summer, mulch plants with straw to keep soil cool and reduce water evaporation by up to 70%.' },
  { id:5, icon:'🌧️', category:'Seasonal', title:'Monsoon Fungal Alert', body:'During rains, spray preventive copper fungicide every 10 days and ensure good drainage around plant roots.' },
  { id:6, icon:'🐝', category:'Pest Control', title:'Attract Beneficial Insects', body:'Plant marigolds or basil near tomatoes to attract ladybirds and lacewings that control aphids and whiteflies.' },
]

export default function TipsCarousel() {
  const [tips, setTips]       = useState(FALLBACK_TIPS)
  const [current, setCurrent] = useState(0)
  const [paused, setPaused]   = useState(false)

  useEffect(() => {
    getFarmingTips(6).then(d => { if (d?.tips?.length) setTips(d.tips) }).catch(() => {})
  }, [])

  // Auto-cycle every 6 s
  useEffect(() => {
    if (paused) return
    const id = setInterval(() => setCurrent(c => (c + 1) % tips.length), 6000)
    return () => clearInterval(id)
  }, [tips.length, paused])

  const tip = tips[current]

  return (
    <div
      className="card"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-4)' }}>
        <p className="section-label">Daily Farmer Tips</p>
        <span style={{ fontSize: '.75rem', color: 'var(--gray-400)' }}>
          {current + 1} / {tips.length}
        </span>
      </div>

      {/* Tip card */}
      <div
        key={tip.id}
        className="animate-fade-in"
        style={{
          background: 'linear-gradient(135deg, var(--green-50), #f0fdf4)',
          border: '1px solid var(--green-200)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--sp-5)',
          minHeight: 130,
        }}
      >
        <div style={{ display: 'flex', gap: 'var(--sp-3)', alignItems: 'flex-start' }}>
          <div style={{
            width: 44, height: 44, borderRadius: 'var(--radius-md)',
            background: 'var(--green-100)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0,
          }}>{tip.icon}</div>
          <div>
            <span className="badge badge-green" style={{ marginBottom: 'var(--sp-1)' }}>
              {tip.category}
            </span>
            <h3 style={{ fontSize: '1rem', marginBottom: 'var(--sp-2)', color: 'var(--green-900)' }}>
              {tip.title}
            </h3>
            <p style={{ fontSize: '.88rem', color: 'var(--gray-600)', lineHeight: 1.6 }}>
              {tip.body}
            </p>
          </div>
        </div>
      </div>

      {/* Dot navigation */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--sp-2)', marginTop: 'var(--sp-4)' }}>
        {tips.map((_, i) => (
          <button key={i} onClick={() => setCurrent(i)} style={{
            width: i === current ? 20 : 8, height: 8,
            borderRadius: 'var(--radius-full)', border: 'none', cursor: 'pointer',
            background: i === current ? 'var(--green-600)' : 'var(--gray-200)',
            transition: 'all var(--dur-base) var(--ease)', padding: 0,
          }} />
        ))}
      </div>

      {/* Prev / Next */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--sp-3)', marginTop: 'var(--sp-3)' }}>
        <button className="btn btn-ghost btn-sm"
          onClick={() => setCurrent(c => (c - 1 + tips.length) % tips.length)}>
          ← Prev
        </button>
        <button className="btn btn-ghost btn-sm"
          onClick={() => setCurrent(c => (c + 1) % tips.length)}>
          Next →
        </button>
      </div>
    </div>
  )
}
