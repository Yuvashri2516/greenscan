import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp, Info, HelpCircle, Activity, ShieldCheck, Thermometer } from 'lucide-react'

export default function DiseaseInsights({ diseaseInfo = null }) {
  const [expandedSection, setExpandedSection] = useState(null)

  if (!diseaseInfo) {
    return (
      <div className="card" style={{ padding: '24px', background: '#fff', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-lg)' }}>
        <p style={{ margin: 0, color: 'var(--gray-500)', fontSize: '0.9rem' }}>Disease information unavailable.</p>
      </div>
    )
  }

  const sections = [
    {
      id: 'symptoms',
      title: 'Symptoms',
      icon: '👁️',
      content: diseaseInfo.symptoms,
      isList: Array.isArray(diseaseInfo.symptoms)
    },
    {
      id: 'causes',
      title: 'Causes & Environmental Triggers',
      icon: '🌡️',
      content: diseaseInfo.causes,
      isList: Array.isArray(diseaseInfo.causes)
    },
    {
      id: 'organic',
      title: 'Organic Treatment',
      icon: '🌱',
      content: diseaseInfo.organic_treatment || diseaseInfo.organic_solutions,
      isList: Array.isArray(diseaseInfo.organic_treatment || diseaseInfo.organic_solutions)
    },
    {
      id: 'chemical',
      title: 'Chemical Treatment',
      icon: '🧪',
      content: diseaseInfo.chemical_treatment || diseaseInfo.chemical_solutions,
      isList: Array.isArray(diseaseInfo.chemical_treatment || diseaseInfo.chemical_solutions)
    },
    {
      id: 'prevention',
      title: 'Preventive Measures',
      icon: '🛡️',
      content: diseaseInfo.preventive_measures || diseaseInfo.prevention,
      isList: Array.isArray(diseaseInfo.preventive_measures || diseaseInfo.prevention)
    },
    {
      id: 'fertilizer',
      title: 'Suitable Fertilizer',
      icon: '⚡',
      content: diseaseInfo.suitable_fertilizer,
      isList: false
    },
    {
      id: 'recovery',
      title: 'Recovery Time',
      icon: '⏱️',
      content: diseaseInfo.recovery_time,
      isList: false
    }
  ]

  const toggleSection = (id) => {
    setExpandedSection(expandedSection === id ? null : id)
  }

  return (
    <div className="card" style={{ padding: '32px', background: '#fff', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)' }}>
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 4px', fontSize: '1.4rem', color: 'var(--green-900)', fontWeight: 800 }}>
          Disease Insights
        </h3>
        <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--gray-500)' }}>
          {diseaseInfo.display_name} — <em>{diseaseInfo.scientific_name || 'Scientific name unavailable'}</em>
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {sections.map((section) => {
          const hasContent = section.content && (section.isList ? section.content.length > 0 : true)
          const displayContent = hasContent ? section.content : 'Information unavailable'
          const isExpanded = expandedSection === section.id

          return (
            <div 
              key={section.id} 
              style={{ 
                border: '1px solid var(--gray-200)', 
                borderRadius: '8px', 
                overflow: 'hidden',
                background: isExpanded ? 'var(--gray-50)' : '#fff',
                transition: 'background-color 0.2s ease'
              }}
            >
              <button
                onClick={() => toggleSection(section.id)}
                style={{
                  width: '100%',
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'left',
                  outline: 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '1.2rem' }}>{section.icon}</span>
                  <span style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--gray-800)' }}>
                    {section.title}
                  </span>
                </div>
                {isExpanded ? <ChevronUp size={18} color="var(--gray-500)" /> : <ChevronDown size={18} color="var(--gray-500)" />}
              </button>

              <AnimatePresence initial={false}>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: 'easeInOut' }}
                  >
                    <div style={{ padding: '0 20px 20px 20px', borderTop: '1px solid var(--gray-100)', paddingTop: '16px' }}>
                      {section.isList ? (
                        <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-700)', fontSize: '0.9rem', lineHeight: '1.6' }}>
                          {displayContent.map((item, idx) => (
                            <li key={idx} style={{ marginBottom: '8px' }}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p style={{ margin: 0, color: 'var(--gray-700)', fontSize: '0.9rem', lineHeight: '1.6' }}>
                          {displayContent}
                        </p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )
        })}
      </div>
    </div>
  )
}
