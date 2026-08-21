import { useEffect, useState } from 'react'
import { motion, animate } from 'framer-motion'

export default function HealthScoreGauge({ score = 100, trafficColor = 'var(--green-700)', trafficDot = '🟢', severity = 'Healthy' }) {
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    // Smooth number count-up animation
    const controls = animate(0, score, {
      duration: 1.5,
      ease: 'easeOut',
      onUpdate: (value) => setDisplayScore(Math.round(value))
    })
    return () => controls.stop()
  }, [score])

  const radius = 60
  const strokeWidth = 10
  const circumference = 2 * Math.PI * radius

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', background: '#fff', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--gray-200)', boxShadow: 'var(--shadow-sm)', flex: '1 1 200px', minWidth: '240px' }}>
      <div style={{ position: 'relative', width: '150px', height: '150px' }}>
        <svg width="100%" height="100%" viewBox="0 0 150 150">
          {/* Track circle */}
          <circle
            cx="75"
            cy="75"
            r={radius}
            fill="none"
            stroke="var(--gray-100)"
            strokeWidth={strokeWidth}
          />
          {/* Animated score circle */}
          <motion.circle
            cx="75"
            cy="75"
            r={radius}
            fill="none"
            stroke={trafficColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference * (1 - score / 100) }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            strokeLinecap="round"
            transform="rotate(-90 75 75)"
          />
        </svg>
        {/* Score text absolute centered */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{ fontSize: '2.2rem', fontWeight: 900, color: 'var(--gray-900)', lineHeight: '1.1' }}>
            {displayScore}
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--gray-400)', fontWeight: 700, letterSpacing: '0.05em' }}>
            / 100
          </span>
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '0.9rem', color: 'var(--gray-500)', fontWeight: 700 }}>Plant Health Score</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', marginTop: '6px', fontSize: '0.85rem', fontWeight: 800, color: trafficColor }}>
          <span>{trafficDot}</span>
          <span>{severity} Severity Level</span>
        </div>
      </div>
    </div>
  )
}
