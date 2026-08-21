// src/components/Header.jsx
import { useState } from 'react'

export default function Header({ activeTab, onTabChange }) {
  const [menuOpen, setMenuOpen] = useState(false)

  const tabs = [
    { id: 'scan',      label: '🔬 Scan',        title: 'Scan Leaf' },
    { id: 'stores',    label: '📍 Stores',       title: 'Find Stores' },
    { id: 'tips',      label: '🌱 Tips',          title: 'Farmer Tips' },
    { id: 'analytics', label: '📊 Analytics',     title: 'AI Analytics' },
    { id: 'research',  label: '🎓 Research',      title: 'AI Research' },
  ]

  return (
    <header style={{
      background: 'linear-gradient(135deg, var(--green-900) 0%, var(--green-700) 100%)',
      boxShadow: '0 2px 20px rgba(27,67,50,.4)',
      position: 'sticky', top: 0, zIndex: 'var(--z-sticky)',
    }}>
      <div className="container" style={{ padding: '0 var(--sp-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>

          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-3)' }}>
            <div style={{
              width: 40, height: 40, borderRadius: 'var(--radius-md)',
              background: 'rgba(255,255,255,.15)', backdropFilter: 'blur(8px)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 22,
            }}>🌿</div>
            <div>
              <div style={{ color: '#fff', fontWeight: 800, fontSize: '1.15rem', lineHeight: 1.1 }}>
                GreenScan
              </div>
              <div style={{ color: 'rgba(255,255,255,.65)', fontSize: '.7rem', fontWeight: 500 }}>
                Smart Plant Health
              </div>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav className="hide-mobile" style={{ display: 'flex', gap: 'var(--sp-1)' }}>
            {tabs.map(t => (
              <button key={t.id}
                onClick={() => onTabChange(t.id)}
                style={{
                  padding: '8px 18px',
                  borderRadius: 'var(--radius-full)',
                  border: 'none',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '.88rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all var(--dur-fast) var(--ease)',
                  background: activeTab === t.id ? 'rgba(255,255,255,.95)' : 'rgba(255,255,255,.12)',
                  color: activeTab === t.id ? 'var(--green-800)' : 'rgba(255,255,255,.85)',
                }}
              >{t.label}</button>
            ))}
          </nav>

          {/* Mobile Hamburger */}
          <button
            className="btn btn-icon"
            style={{ background: 'rgba(255,255,255,.15)', color: '#fff', display: 'none' }}
            onClick={() => setMenuOpen(v => !v)}
            aria-label="Toggle menu"
          >☰</button>

          <style>{`
            @media (max-width: 768px) {
              .hide-mobile { display: none !important; }
              .btn-icon { display: flex !important; }
            }
            @media (min-width: 769px) { .btn-icon { display: none !important; } }
          `}</style>
        </div>

        {/* Mobile Dropdown */}
        {menuOpen && (
          <div style={{
            paddingBottom: 'var(--sp-4)',
            display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)',
          }}>
            {tabs.map(t => (
              <button key={t.id}
                onClick={() => { onTabChange(t.id); setMenuOpen(false) }}
                style={{
                  padding: '10px 16px', borderRadius: 'var(--radius-md)',
                  border: 'none', fontFamily: 'var(--font-sans)',
                  fontSize: '.92rem', fontWeight: 600, cursor: 'pointer',
                  textAlign: 'left',
                  background: activeTab === t.id ? 'rgba(255,255,255,.9)' : 'rgba(255,255,255,.12)',
                  color: activeTab === t.id ? 'var(--green-800)' : '#fff',
                }}
              >{t.label}</button>
            ))}
          </div>
        )}
      </div>
    </header>
  )
}
