import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Calculator, Beaker, ShieldAlert, CheckCircle2, AlertTriangle, RefreshCw, Loader2 } from 'lucide-react'
import { calculateDosage } from '../api'

const DISEASE_OPTIONS = [
  { value: 'tomato_Early blight', label: 'Tomato — Early Blight' },
  { value: 'tomato_Late blight',  label: 'Tomato — Late Blight' },
  { value: 'tomato_healthy',      label: 'Tomato — Healthy Maintenance' },
]

const SEVERITY_OPTIONS = [
  { value: 'Mild',     label: 'Mild (< 15% leaf area affected)' },
  { value: 'Moderate', label: 'Moderate (15 – 40%)' },
  { value: 'Severe',   label: 'Severe (> 40%)' },
]

const UNIT_OPTIONS = [
  { value: 'acres',    label: 'Acres' },
  { value: 'hectares', label: 'Hectares' },
  { value: 'sqm',      label: 'Square Meters (m²)' },
]

export default function DosageCalculator({ initialDisease = 'tomato_Early blight', initialSeverity = 'Moderate' }) {
  const [disease,   setDisease]   = useState(initialDisease)
  const [severity,  setSeverity]  = useState(initialSeverity)
  const [areaValue, setAreaValue] = useState('')
  const [areaUnit,  setAreaUnit]  = useState('acres')
  const [result,    setResult]    = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)
  const [validationMsg, setValidationMsg] = useState(null)

  // ── Client-side validation ──────────────────────────────────────────────────
  const validate = () => {
    const val = parseFloat(areaValue)
    if (areaValue === '' || areaValue === null || isNaN(val)) {
      setValidationMsg('Please enter a valid field area.')
      return false
    }
    if (val <= 0) {
      setValidationMsg('Field area must be greater than zero.')
      return false
    }
    if (val > 100000) {
      setValidationMsg('Field area seems unrealistically large. Please re-check the value.')
      return false
    }
    setValidationMsg(null)
    return true
  }

  const handleCalculate = async (e) => {
    if (e) e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await calculateDosage({
        disease,
        severity,
        area_value: parseFloat(areaValue),
        area_unit: areaUnit,
      })
      setResult(res)
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const urgencyColor = (urgency = '') => {
    if (urgency.startsWith('HIGH'))          return 'var(--accent-red, #ef4444)'
    if (urgency.startsWith('MEDIUM'))        return 'var(--accent-orange, #f97316)'
    return 'var(--green-700, #15803d)'
  }

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
          <Calculator size={28} />
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--gray-900)' }}>
            🧪 Precision Treatment &amp; Dosage Calculator
          </h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gray-500)', fontSize: '0.9rem' }}>
            Calculate exact fungicide / pesticide quantities &amp; water dilution per acre
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleCalculate} noValidate style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '8px' }}>
        {/* Disease */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '6px' }}>
            Target Disease
          </label>
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            className="input"
            style={{ width: '100%' }}
          >
            {DISEASE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* Severity */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '6px' }}>
            Infection Severity
          </label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="input"
            style={{ width: '100%' }}
          >
            {SEVERITY_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* Area value */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '6px' }}>
            Land Area
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            placeholder="e.g. 2.5"
            value={areaValue}
            onChange={(e) => { setAreaValue(e.target.value); setValidationMsg(null) }}
            className={`input${validationMsg ? ' input-error' : ''}`}
            style={{ width: '100%', borderColor: validationMsg ? 'var(--accent-red, #ef4444)' : undefined }}
          />
        </div>

        {/* Area unit */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '6px' }}>
            Unit
          </label>
          <select
            value={areaUnit}
            onChange={(e) => setAreaUnit(e.target.value)}
            className="input"
            style={{ width: '100%' }}
          >
            {UNIT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* Submit */}
        <div style={{ display: 'flex', alignItems: 'flex-end', gridColumn: '1 / -1' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
          >
            {loading ? <><Loader2 size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} /> Calculating…</> : 'Calculate Dosage &amp; Dilution'}
          </button>
        </div>
      </form>

      {/* Validation message */}
      <AnimatePresence>
        {validationMsg && (
          <motion.div
            key="val-msg"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-red, #ef4444)', fontSize: '0.85rem', marginBottom: '16px' }}
          >
            <AlertTriangle size={16} /> {validationMsg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* API Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            key="err-msg"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ background: '#fff3f3', border: '1px solid #fca5a5', borderRadius: 'var(--radius-md)', padding: '14px 16px', marginBottom: '16px', display: 'flex', alignItems: 'flex-start', gap: '10px' }}
          >
            <AlertTriangle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <p style={{ margin: 0, fontWeight: 600, color: '#991b1b', fontSize: '0.9rem' }}>Calculation Error</p>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div className="skeleton skeleton-title" style={{ width: '40%', margin: 0 }} />
              <div className="skeleton" style={{ width: '80px', height: '22px', borderRadius: 'var(--radius-full)' }} />
            </div>
            <div className="skeleton skeleton-text" style={{ width: '25%', marginBottom: '20px' }} />

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              <div className="card" style={{ padding: '16px', borderLeft: '4px solid var(--gray-200)' }}>
                <div className="skeleton skeleton-title" style={{ width: '60%', height: '14px' }} />
                <div className="skeleton skeleton-text" style={{ width: '40%' }} />
                <div className="skeleton skeleton-text" style={{ width: '70%', height: '16px' }} />
              </div>
              <div className="card" style={{ padding: '16px', borderLeft: '4px solid var(--gray-200)' }}>
                <div className="skeleton skeleton-title" style={{ width: '60%', height: '14px' }} />
                <div className="skeleton skeleton-text" style={{ width: '40%' }} />
                <div className="skeleton skeleton-text" style={{ width: '70%', height: '16px' }} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            key="results"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            style={{ background: 'var(--gray-50)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--gray-200)' }}
          >
            {/* Summary header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <h4 style={{ margin: 0, color: 'var(--gray-900)' }}>📋 Dosage Recommendation Summary</h4>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: urgencyColor(result.urgency), background: '#fff', border: '1px solid var(--gray-200)', padding: '4px 10px', borderRadius: 'var(--radius-full)' }}>
                {result.urgency}
              </span>
            </div>

            <p style={{ margin: '0 0 16px', fontSize: '0.85rem', color: 'var(--gray-500)' }}>
              Area: <strong>{result.original_area}</strong> → <strong>{result.area_acres} acres</strong>
            </p>

            {/* Treatment cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              {/* Chemical */}
              <div style={{ background: '#fff', padding: '16px', borderRadius: 'var(--radius-md)', borderLeft: '4px solid var(--blue-500)' }}>
                <h5 style={{ margin: '0 0 6px', color: 'var(--gray-700)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Beaker size={16} /> Chemical Fungicide Option
                </h5>
                <p style={{ margin: '4px 0', fontSize: '0.9rem', fontWeight: 600 }}>{result.chemical_treatment.active_ingredient}</p>
                <p style={{ margin: 0, color: 'var(--blue-600, #2563eb)', fontWeight: 700 }}>
                  Total Needed: {result.chemical_treatment.total_quantity}
                </p>
                <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                  Mix: {result.chemical_treatment.concentration}
                </p>
              </div>

              {/* Organic */}
              <div style={{ background: '#fff', padding: '16px', borderRadius: 'var(--radius-md)', borderLeft: '4px solid var(--green-600)' }}>
                <h5 style={{ margin: '0 0 6px', color: 'var(--gray-700)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} color="var(--green-600)" /> Organic Bio-Treatment
                </h5>
                <p style={{ margin: '4px 0', fontSize: '0.9rem', fontWeight: 600 }}>{result.organic_treatment.active_ingredient}</p>
                <p style={{ margin: 0, color: 'var(--green-700)', fontWeight: 700 }}>
                  Total Needed: {result.organic_treatment.total_quantity}
                </p>
                <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                  Mix: {result.organic_treatment.concentration}
                </p>
              </div>
            </div>

            {/* Spray specifications */}
            <div style={{ background: '#fff', padding: '16px', borderRadius: 'var(--radius-md)', fontSize: '0.85rem' }}>
              <p style={{ margin: '0 0 10px', fontWeight: 700, color: 'var(--gray-800)' }}>
                💧 Spray Specifications &amp; Safety Protocols:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '8px', marginBottom: '12px' }}>
                <div style={{ background: 'var(--gray-50)', padding: '10px', borderRadius: '8px' }}>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--gray-500)' }}>Total Water Required</p>
                  <p style={{ margin: '2px 0 0', fontWeight: 700, color: 'var(--blue-600, #2563eb)' }}>
                    {result.spray_specifications.total_water_required_liters} L
                  </p>
                </div>
                <div style={{ background: 'var(--gray-50)', padding: '10px', borderRadius: '8px' }}>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--gray-500)' }}>Pre-Harvest Interval (PHI)</p>
                  <p style={{ margin: '2px 0 0', fontWeight: 700, color: 'var(--gray-800)' }}>
                    {result.spray_specifications.pre_harvest_interval_days} Days
                  </p>
                </div>
                <div style={{ background: 'var(--gray-50)', padding: '10px', borderRadius: '8px' }}>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--gray-500)' }}>Next Application In</p>
                  <p style={{ margin: '2px 0 0', fontWeight: 700, color: 'var(--gray-800)' }}>
                    {result.spray_specifications.next_application_in_days} Days
                  </p>
                </div>
              </div>
              <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-600)' }}>
                {result.spray_specifications.safety_instructions.map((inst, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{inst}</li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
