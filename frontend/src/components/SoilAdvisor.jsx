import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sprout, AlertCircle, CheckCircle2, AlertTriangle, RefreshCw, Loader2, Droplets, Leaf } from 'lucide-react'
import { analyzeSoilHealth } from '../api'

const SOIL_TYPE_OPTIONS = [
  { value: 'Loam',  label: 'Loam (Optimal)' },
  { value: 'Clay',  label: 'Clay' },
  { value: 'Sandy', label: 'Sandy' },
  { value: 'Silt',  label: 'Silt' },
]

const NPK_PARAMS = [
  { key: 'nitrogen',   setter: 'setNitrogen',   label: 'Nitrogen (N)',   unit: 'ppm', min: 20,  max: 300, step: 5,  state: null },
  { key: 'phosphorus', setter: 'setPhosphorus', label: 'Phosphorus (P)', unit: 'ppm', min: 5,   max: 100, step: 5,  state: null },
  { key: 'potassium',  setter: 'setPotassium',  label: 'Potassium (K)',  unit: 'ppm', min: 50,  max: 400, step: 10, state: null },
]

function ScoreCircle({ score, color }) {
  return (
    <div style={{
      background: color,
      color: '#fff',
      width: '56px',
      height: '56px',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 800,
      fontSize: '1.25rem',
      flexShrink: 0,
    }}>
      {score}
    </div>
  )
}

function StatusBadge({ status }) {
  const isOptimal = status === 'Optimal'
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: 'var(--radius-full)',
      fontSize: '0.78rem',
      fontWeight: 600,
      background: isOptimal ? '#dcfce7' : '#fff3cd',
      color: isOptimal ? '#166534' : '#92400e',
      border: `1px solid ${isOptimal ? '#86efac' : '#fcd34d'}`,
    }}>
      {status}
    </span>
  )
}

export default function SoilAdvisor() {
  const [ph,         setPh]         = useState(6.5)
  const [nitrogen,   setNitrogen]   = useState(140)
  const [phosphorus, setPhosphorus] = useState(45)
  const [potassium,  setPotassium]  = useState(210)
  const [moisture,   setMoisture]   = useState(45)
  const [soilType,   setSoilType]   = useState('Loam')
  const [result,     setResult]     = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await analyzeSoilHealth({
        ph:         parseFloat(ph),
        nitrogen:   parseFloat(nitrogen),
        phosphorus: parseFloat(phosphorus),
        potassium:  parseFloat(potassium),
        moisture:   parseFloat(moisture),
        soil_type:  soilType,
      })
      setResult(res)
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const paramSetters = { nitrogen: setNitrogen, phosphorus: setPhosphorus, potassium: setPotassium }
  const paramValues  = { nitrogen, phosphorus, potassium }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
      style={{ padding: '32px' }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <div style={{ background: 'var(--green-100)', padding: '10px', borderRadius: '12px', color: 'var(--green-700)' }}>
          <Sprout size={28} />
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--gray-900)' }}>
            🌱 Soil &amp; Environmental Health Advisor
          </h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gray-500)', fontSize: '0.9rem' }}>
            N-P-K nutrient balancing, pH adjustment &amp; organic soil remediation
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleAnalyze} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '24px' }}>

        {/* pH */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)' }}>Soil pH Level</label>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--green-700)' }}>{parseFloat(ph).toFixed(1)}</span>
          </div>
          <input
            type="range"
            min="4.0" max="9.0" step="0.1"
            value={ph}
            onChange={(e) => setPh(e.target.value)}
            style={{ width: '100%' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--gray-400)', marginTop: '2px' }}>
            <span>4.0 (Acid)</span><span>9.0 (Alkaline)</span>
          </div>
        </div>

        {/* N, P, K sliders */}
        {NPK_PARAMS.map(({ key, label, unit, min, max, step }) => (
          <div key={key}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)' }}>{label} <span style={{ color: 'var(--gray-400)', fontWeight: 400 }}>{unit}</span></label>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--green-700)' }}>{paramValues[key]}</span>
            </div>
            <input
              type="range"
              min={min} max={max} step={step}
              value={paramValues[key]}
              onChange={(e) => paramSetters[key](e.target.value)}
              style={{ width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--gray-400)', marginTop: '2px' }}>
              <span>{min}</span><span>{max}</span>
            </div>
          </div>
        ))}

        {/* Moisture */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)' }}>
              <Droplets size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
              Soil Moisture
            </label>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--blue-600, #2563eb)' }}>{moisture}%</span>
          </div>
          <input
            type="range"
            min="10" max="90" step="5"
            value={moisture}
            onChange={(e) => setMoisture(e.target.value)}
            style={{ width: '100%' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--gray-400)', marginTop: '2px' }}>
            <span>10% Dry</span><span>90% Saturated</span>
          </div>
        </div>

        {/* Soil type */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '4px' }}>
            Soil Texture Type
          </label>
          <select
            value={soilType}
            onChange={(e) => setSoilType(e.target.value)}
            className="input"
            style={{ width: '100%' }}
          >
            {SOIL_TYPE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* Submit */}
        <div style={{ gridColumn: '1 / -1' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {loading
              ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> Analyzing Soil Chemistry…</>
              : 'Run Soil Health Diagnostics'
            }
          </button>
        </div>
      </form>

      {/* API error */}
      <AnimatePresence>
        {error && (
          <motion.div
            key="soil-error"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ background: '#fff3f3', border: '1px solid #fca5a5', borderRadius: 'var(--radius-md)', padding: '14px 16px', marginBottom: '16px', display: 'flex', alignItems: 'flex-start', gap: '10px' }}
          >
            <AlertTriangle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontWeight: 600, color: '#991b1b', fontSize: '0.9rem' }}>Analysis Error</p>
              <p style={{ margin: '4px 0 0', color: '#b91c1c', fontSize: '0.85rem' }}>{error}</p>
            </div>
            <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#b91c1c' }}>
              <RefreshCw size={16} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Skeleton */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ background: 'var(--gray-50)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--gray-200)', marginTop: '24px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
              <div className="skeleton skeleton-circle" />
              <div style={{ flex: 1 }}>
                <div className="skeleton skeleton-title" style={{ width: '30%', margin: 0 }} />
                <div className="skeleton skeleton-text" style={{ width: '45%', margin: 0 }} />
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} style={{ background: '#fff', padding: '12px', borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div className="skeleton skeleton-text" style={{ width: '60%', height: '10px' }} />
                  <div className="skeleton skeleton-title" style={{ width: '40%', height: '18px', margin: 0 }} />
                  <div className="skeleton" style={{ width: '50px', height: '16px', borderRadius: 'var(--radius-full)' }} />
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            key="soil-results"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            style={{ background: 'var(--gray-50)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--gray-200)' }}
          >
            {/* Score header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <ScoreCircle score={result.overall_score} color={result.badge_color} />
                <div>
                  <h4 style={{ margin: 0, color: 'var(--gray-900)' }}>{result.rating}</h4>
                  <p style={{ margin: '2px 0 0', fontSize: '0.85rem', color: 'var(--gray-500)' }}>Soil Chemistry Quality Score</p>
                </div>
              </div>
              <div style={{ background: '#fff', padding: '6px 14px', borderRadius: 'var(--radius-full)', border: '1px solid var(--gray-300)', fontSize: '0.85rem', fontWeight: 600 }}>
                Texture: {result.parameters.soil_type}
              </div>
            </div>

            {/* NPK + pH parameter grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '20px' }}>
              {[
                { label: 'pH', param: result.parameters.ph },
                { label: 'Nitrogen (N)', param: result.parameters.nitrogen_ppm },
                { label: 'Phosphorus (P)', param: result.parameters.phosphorus_ppm },
                { label: 'Potassium (K)', param: result.parameters.potassium_ppm },
                { label: 'Moisture', param: result.parameters.moisture_pct },
              ].map(({ label, param }) => (
                <div key={label} style={{ background: '#fff', padding: '12px', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <p style={{ margin: '0 0 6px', fontSize: '0.78rem', color: 'var(--gray-500)', fontWeight: 600 }}>{label}</p>
                  <p style={{ margin: '0 0 6px', fontWeight: 700, color: 'var(--gray-800)', fontSize: '1.1rem' }}>{param.value}</p>
                  <StatusBadge status={param.status} />
                </div>
              ))}
            </div>

            {/* Deficiencies */}
            {result.deficiencies && result.deficiencies.length > 0 && (
              <div style={{ background: '#fff8e1', borderLeft: '4px solid var(--accent-orange, #f97316)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                <h5 style={{ margin: '0 0 8px', color: 'var(--gray-900)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={18} color="var(--accent-orange, #f97316)" /> Diagnosed Deficiencies &amp; Risk Factors:
                </h5>
                <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-700)', fontSize: '0.85rem' }}>
                  {result.deficiencies.map((def, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{def}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Organic amendments */}
            {result.organic_amendments && result.organic_amendments.length > 0 && (
              <div style={{ background: '#e8f5e9', borderLeft: '4px solid var(--green-600)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                <h5 style={{ margin: '0 0 8px', color: 'var(--gray-900)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={18} color="var(--green-600)" /> Recommended Organic Soil Amendments:
                </h5>
                <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-700)', fontSize: '0.85rem' }}>
                  {result.organic_amendments.map((amend, idx) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{amend}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suitable crops */}
            {result.suitable_crops && result.suitable_crops.length > 0 && (
              <div style={{ background: '#fff', padding: '14px 16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)' }}>
                <p style={{ margin: '0 0 8px', fontWeight: 700, color: 'var(--gray-800)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Leaf size={16} color="var(--green-600)" /> Suitable Crops for Current Soil Profile:
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {result.suitable_crops.map((crop, idx) => (
                    <span key={idx} style={{ background: '#dcfce7', color: '#166534', padding: '3px 10px', borderRadius: 'var(--radius-full)', fontSize: '0.82rem', fontWeight: 600, border: '1px solid #86efac' }}>
                      {crop}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
