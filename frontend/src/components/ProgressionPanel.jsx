// src/components/ProgressionPanel.jsx
import React from 'react'

export default function ProgressionPanel({ progression }) {
  if (!progression || progression.risk_score === 0) return null

  const { risk_score, warning_level, forecast_7d, days_to_severe } = progression

  const getLevelColor = (level) => {
    switch (level) {
      case 'Low': return 'var(--green-500)';
      case 'Medium': return 'var(--yellow-500)';
      case 'High': return 'var(--orange-500)';
      case 'Critical': return 'var(--red-600)';
      default: return 'var(--gray-400)';
    }
  }

  // Calculate SVG polyline points for sparkline
  const maxVal = Math.max(...forecast_7d, 10);
  const points = forecast_7d.map((val, i) => {
    const x = (i / 6) * 100;
    const y = 40 - (val / maxVal) * 35;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="card" style={{ padding: 'var(--sp-5)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-4)' }}>
        <h4 style={{ margin: 0, fontSize: '.9rem', color: 'var(--gray-600)' }}>Disease Progression Forecast</h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-2)' }}>
          <span style={{ fontSize: '.75rem', fontWeight: 600, color: getLevelColor(warning_level) }}>
            {warning_level.toUpperCase()} RISK
          </span>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: getLevelColor(warning_level) }} className="animate-pulse" />
        </div>
      </div>

      <div style={{ background: 'var(--gray-50)', padding: 'var(--sp-4)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--sp-4)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--sp-2)' }}>
          <span style={{ fontSize: '.8rem', color: 'var(--gray-500)' }}>7-Day Spread Projection</span>
          <span style={{ fontSize: '.8rem', fontWeight: 600, color: 'var(--gray-700)' }}>
            {forecast_7d[0]}% → {forecast_7d[6]}%
          </span>
        </div>
        
        {/* Sparkline SVG */}
        <svg viewBox="0 0 100 40" style={{ width: '100%', height: 40, overflow: 'visible' }}>
          <path d={`M ${points}`} fill="none" stroke={getLevelColor(warning_level)} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          {forecast_7d.map((val, i) => (
            <circle key={i} cx={(i / 6) * 100} cy={40 - (val / maxVal) * 35} r="2" fill={getLevelColor(warning_level)} />
          ))}
        </svg>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'var(--sp-1)', fontSize: '.7rem', color: 'var(--gray-400)' }}>
          <span>Today</span>
          <span>Day 7</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 'var(--sp-3)' }}>
        <div style={{ flex: 1, background: 'var(--gray-50)', padding: 'var(--sp-3)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
          <p style={{ fontSize: '.65rem', color: 'var(--gray-400)', textTransform: 'uppercase', marginBottom: 2 }}>Risk Score</p>
          <p style={{ fontSize: '1.1rem', fontWeight: 700, color: getLevelColor(warning_level) }}>{risk_score}/100</p>
        </div>
        <div style={{ flex: 1, background: 'var(--gray-50)', padding: 'var(--sp-3)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
          <p style={{ fontSize: '.65rem', color: 'var(--gray-400)', textTransform: 'uppercase', marginBottom: 2 }}>Status Alert</p>
          <p style={{ fontSize: '.85rem', fontWeight: 600, color: 'var(--gray-700)' }}>
            {days_to_severe > 0 ? `Severe in ${days_to_severe} days` : 'Stable / Severe'}
          </p>
        </div>
      </div>
    </div>
  )
}
