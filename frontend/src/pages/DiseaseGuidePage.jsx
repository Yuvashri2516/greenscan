import { useEffect, useState } from 'react'
import { getDiseaseCatalog } from '../api/index.js'
import { motion } from 'framer-motion'
import { AlertCircle, BookOpen, Shield, HelpCircle, Check, Info } from 'lucide-react'
import '../index.css'

export default function DiseaseGuidePage() {
  const [diseases, setDiseases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDiseases()
  }, [])

  const fetchDiseases = async () => {
    try {
      setLoading(true)
      const data = await getDiseaseCatalog()
      setDiseases(data.diseases || [])
      setError(null)
    } catch (err) {
      console.error(err)
      // Fallback local catalog if backend is unavailable
      setDiseases([
        {
          key: "tomato_healthy",
          display_name: "Healthy Tomato",
          scientific_name: "Solanum lycopersicum",
          symptoms: "Vibrant green leaves, robust stem, clear vascular tissue, no spots or lesions.",
          causes: "Optimal nutritional balance, proper soil drainage, clean environmental conditions.",
          organic_treatment: "Maintain organic soil compost, neem oil foliar spray bi-weekly for prevention.",
          chemical_treatment: "No chemical treatment required.",
          preventive_measures: "Ensure proper row spacing (45-60cm), crop rotation, drip irrigation at soil level.",
          suitable_fertilizer: "Balanced N-P-K (10-10-10) fertilizer during foliage growth, calcium nitrate during flowering.",
          recovery_time: "N/A (Plant is healthy)"
        },
        {
          key: "tomato_Early blight",
          display_name: "Tomato Early Blight",
          scientific_name: "Alternaria solani",
          symptoms: "Concentric ringed brown/black spots (target board pattern) on older lower leaves, leaf yellowing.",
          causes: "Fungal pathogen Alternaria solani surviving in soil debris; favored by warm temperatures (24-29°C) and high humidity.",
          organic_treatment: "Spray copper sulfate solution or Trichoderma harzianum; prune infected lower leaves.",
          chemical_treatment: "Apply Chlorothalonil or Mancozeb fungicide every 7-10 days.",
          preventive_measures: "Rotate crops with non-solanaceous plants, mulch around base to prevent soil splash, avoid overhead watering.",
          suitable_fertilizer: "High Potassium (K) fertilizer to boost disease resistance; minimize excess nitrogen.",
          recovery_time: "10 to 14 days with active fungicidal management."
        },
        {
          key: "tomato_Late blight",
          display_name: "Tomato Late Blight",
          scientific_name: "Phytophthora infestans",
          symptoms: "Water-soaked dark lesions on leaves with white fuzzy fungal growth underneath in humid conditions, rapid wilting.",
          causes: "Oomycete pathogen Phytophthora infestans spread by wind and rain; thrives in cool (15-22°C), wet weather.",
          organic_treatment: "Baking soda solution (1 tbsp/gal water) with horticultural oil; immediate removal and destruction of heavily infected foliage.",
          chemical_treatment: "Systemic fungicides such as Metalaxyl, Dimethomorph, or Copper Hydroxide within 24-48 hours.",
          preventive_measures: "Plant resistant cultivars (e.g., Defiant PHR), destroy volunteer tomato/potato plants, maintain rapid foliage drying.",
          suitable_fertilizer: "Potassium silicate spray to strengthen cell walls; avoid high nitrogen during wet spells.",
          recovery_time: "14 to 21 days; requires immediate containment to prevent total crop loss."
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const getSeverityTrafficColor = (key) => {
    if (key.includes('healthy')) return 'var(--green-600)'
    if (key.includes('Early')) return 'var(--accent-orange)'
    return 'var(--accent-red)'
  }

  const formatList = (str) => {
    if (!str) return []
    return str.split(/;|\./).map(x => x.strip ? x.strip() : x.trim()).filter(Boolean)
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0 }} 
      transition={{ duration: 0.5 }}
      style={{ minHeight: '100vh', background: 'var(--green-50)', padding: 'var(--sp-8) 0' }}
    >
      <div className="container" style={{ maxWidth: '1000px' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--sp-8)' }}>
          <h1 style={{ color: 'var(--green-900)' }}>Tomato Disease Library</h1>
          <p style={{ color: 'var(--gray-600)', marginTop: '8px' }}>
            Comprehensive guide to signs, symptoms, causes, and control solutions for tomato leaf conditions.
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {[1, 2].map((i) => (
              <div key={i} className="card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--gray-200)', paddingBottom: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <div className="skeleton skeleton-title" style={{ width: '40%' }} />
                    <div className="skeleton skeleton-text" style={{ width: '25%' }} />
                  </div>
                  <div className="skeleton" style={{ width: '100px', height: '28px', borderRadius: '9999px' }} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                  <div>
                    <div className="skeleton skeleton-title" style={{ width: '30%', height: '14px' }} />
                    <div className="skeleton skeleton-text" />
                    <div className="skeleton skeleton-text" style={{ width: '85%' }} />
                  </div>
                  <div>
                    <div className="skeleton skeleton-title" style={{ width: '30%', height: '14px' }} />
                    <div className="skeleton skeleton-text" />
                    <div className="skeleton skeleton-text" style={{ width: '85%' }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Catalog List */}
        {!loading && diseases.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            {diseases.map((d) => (
              <div 
                key={d.key} 
                className="card" 
                style={{ 
                  padding: '32px', 
                  borderLeft: `8px solid ${getSeverityTrafficColor(d.key)}`,
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', borderBottom: '1px solid var(--gray-200)', paddingBottom: '16px', marginBottom: '20px' }}>
                  <div>
                    <h2 style={{ color: 'var(--gray-900)', margin: 0, fontSize: '1.6rem' }}>{d.display_name}</h2>
                    <p style={{ color: 'var(--gray-500)', fontStyle: 'italic', margin: '4px 0 0' }}>{d.scientific_name}</p>
                  </div>
                  <span className="badge" style={{ background: getSeverityTrafficColor(d.key) + '15', color: getSeverityTrafficColor(d.key), padding: '6px 14px' }}>
                    {d.key.includes('healthy') ? '🟢 Healthy' : d.key.includes('Early') ? '🟠 Moderate Risk' : '🔴 Severe Risk'}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                  {/* Left Column: Symptoms & Causes */}
                  <div>
                    <div style={{ marginBottom: '18px' }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', margin: '0 0 8px' }}>
                        <BookOpen size={16} color="var(--green-700)" /> Key Symptoms
                      </h4>
                      <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.5' }}>{d.symptoms}</p>
                    </div>

                    <div style={{ marginBottom: '18px' }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', margin: '0 0 8px' }}>
                        <HelpCircle size={16} color="var(--green-700)" /> Common Causes
                      </h4>
                      <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.5' }}>{d.causes}</p>
                    </div>
                  </div>

                  {/* Right Column: Treatments */}
                  <div>
                    <div style={{ marginBottom: '18px' }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', margin: '0 0 8px' }}>
                        🌱 Organic Remedies
                      </h4>
                      <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.5' }}>{d.organic_treatment}</p>
                    </div>

                    <div style={{ marginBottom: '18px' }}>
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', margin: '0 0 8px' }}>
                        🧪 Chemical Control
                      </h4>
                      <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.5' }}>{d.chemical_treatment}</p>
                    </div>
                  </div>
                </div>

                {/* Prevention Footer */}
                <div style={{ marginTop: '20px', padding: '20px', background: 'var(--gray-50)', borderRadius: '12px', border: '1px solid var(--gray-200)' }}>
                  <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', margin: '0 0 10px' }}>
                    <Shield size={16} color="var(--accent-blue)" /> Preventive Measures
                  </h4>
                  <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', margin: 0, lineHeight: '1.5' }}>{d.preventive_measures}</p>
                </div>

                {/* Additional Agronomic Details */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginTop: '20px', fontSize: '0.85rem' }}>
                  <div style={{ background: 'var(--green-100)', color: 'var(--green-900)', padding: '6px 14px', borderRadius: '30px' }}>
                    <strong>🌾 Suitable Fertilizer:</strong> {d.suitable_fertilizer}
                  </div>
                  <div style={{ background: 'var(--green-100)', color: 'var(--green-900)', padding: '6px 14px', borderRadius: '30px' }}>
                    <strong>⏳ Recovery Time:</strong> {d.recovery_time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
