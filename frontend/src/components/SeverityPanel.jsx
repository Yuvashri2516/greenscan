import React from 'react'
import { Activity, ShieldAlert, Heart, Info } from 'lucide-react'
import '../index.css'

export default function SeverityPanel({ gsaMetrics }) {
  const gsa = gsaMetrics || {}
  const healthScore = gsa.plant_health_score ?? 100
  const trafficLight = gsa.traffic_light || '🟢'
  const severityLevel = gsa.severity_level || 'Healthy'
  const affectedAreaPct = gsa.attention_affected_region_percent ?? gsa.affected_area_pct ?? 0
  const treatmentPriority = gsa.treatment_priority || 'No chemical intervention needed. Monitor crop health routinely.'

  const getSeverityColor = (score) => {
    if (score >= 90) return 'var(--green-700)'
    if (score >= 70) return '#FBC02D' // Yellow
    if (score >= 40) return 'var(--accent-orange)' // Orange
    return 'var(--accent-red)' // Red
  }

  const severityColor = getSeverityColor(healthScore)

  return (
    <div className="card" style={{ padding: '32px', background: '#fff', borderRadius: '20px', border: '1px solid var(--gray-200)' }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid var(--gray-200)', paddingBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--green-900)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={20} color="var(--green-800)" /> Plant Health Status
        </h3>
        <span style={{ fontSize: '1.5rem' }}>{trafficLight}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '32px', alignItems: 'center' }}>
        {/* Health Gauge */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ position: 'relative', width: 140, height: 140 }}>
            <svg width="140" height="140" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="var(--gray-100)" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none" stroke={severityColor} strokeWidth="8"
                strokeDasharray={2 * Math.PI * 42}
                strokeDashoffset={2 * Math.PI * 42 * (1 - healthScore / 100)}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
                style={{ transition: 'stroke-dashoffset 1s ease-out' }}
              />
            </svg>
            <div style={{
              position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
            }}>
              <span style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--gray-900)' }}>{healthScore}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--gray-400)', fontWeight: 700, letterSpacing: '0.05em' }}>HEALTH SCORE</span>
            </div>
          </div>
          <p style={{ marginTop: '16px', fontWeight: 800, color: severityColor, fontSize: '1.1rem', margin: '12px 0 0', textTransform: 'capitalize' }}>
            {severityLevel} Stage
          </p>
          <div style={{ display: 'flex', gap: '6px', marginTop: '8px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--gray-400)', textTransform: 'uppercase' }}>
            <span>Healthy</span> • <span>Mild</span> • <span>Moderate</span> • <span>Severe</span>
          </div>
        </div>

        {/* Statistical Summary */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Card 1 */}
          <div style={{ background: 'var(--gray-50)', padding: '16px', borderRadius: '12px', border: '1px solid var(--gray-100)' }}>
            <p style={{ margin: '0 0 6px', fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldAlert size={14} color="var(--green-700)" /> Attention-Affected Region
            </p>
            <p style={{ margin: '0 0 6px', fontSize: '1.5rem', fontWeight: 800, color: 'var(--gray-900)' }}>
              {affectedAreaPct.toFixed(1)}%
            </p>
            <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--gray-500)', lineHeight: 1.4 }}>
              This represents the proportion of the detected leaf area associated with stronger model activation. It is <strong>not</strong> the exact physical disease lesion area.
            </p>
          </div>

          {/* Card 2 */}
          <div style={{ background: 'var(--gray-50)', padding: '16px', borderRadius: '12px', border: '1px solid var(--gray-100)' }}>
            <p style={{ margin: '0 0 4px', fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Heart size={14} color="var(--green-700)" /> Plant Health Status Explanation
            </p>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--gray-600)', lineHeight: '1.45' }}>
              GreenScan detected disease-related visual patterns with a <strong>{severityLevel.toLowerCase()}</strong> level of estimated attention-affected area on the leaf surfaces.
            </p>
          </div>
        </div>
      </div>

      {/* Priority Protocol */}
      {treatmentPriority && (
        <div style={{ marginTop: '24px', padding: '18px', background: '#F1F8E9', borderRadius: '12px', borderLeft: `5px solid ${severityColor}`, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <h4 style={{ margin: 0, color: 'var(--green-900)', fontSize: '0.95rem', fontWeight: 700 }}>
            ⚠️ GSA Treatment Priority Protocol
          </h4>
          <p style={{ margin: 0, color: 'var(--gray-800)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            {treatmentPriority}
          </p>
        </div>
      )}
    </div>
  )
}
