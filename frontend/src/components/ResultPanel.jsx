import { useState } from 'react'
import { motion } from 'framer-motion'
import HealthScoreGauge from './HealthScoreGauge'
import DiseaseInsights from './DiseaseInsights'
import { AlertTriangle, AlertOctagon, CheckCircle2, Info } from 'lucide-react'
import '../index.css'

export default function ResultPanel({ result }) {
  const [activeTab, setActiveTab] = useState('overlay')

  if (!result || !result.disease_info) return null

  // Image quality safety check
  if (result.is_reliable === false) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }} 
        animate={{ opacity: 1, scale: 1 }} 
        className="card" 
        style={{ padding: '0', overflow: 'hidden', border: `1px solid var(--accent-orange)30` }}
      >
        <div style={{ background: '#fff8e1', padding: '24px 32px', display: 'flex', alignItems: 'center', gap: '16px', borderBottom: `1px solid var(--accent-orange)20` }}>
          <AlertTriangle size={28} color="var(--accent-orange)" />
          <div>
            <h2 style={{ margin: 0, color: 'var(--gray-900)', fontSize: '1.3rem', fontWeight: 800 }}>Low Image Quality Warning</h2>
          </div>
        </div>
        <div style={{ padding: '32px' }}>
          <p style={{ color: 'var(--gray-700)', fontSize: '0.92rem', marginBottom: '24px', lineHeight: 1.6 }}>
            {result.recommendations?.safety_warning || "Unable to supply a precise crop diagnosis. The leaf image is either blurry, poorly lit, or contains excessive background elements."}
          </p>
          <div style={{ background: 'var(--gray-50)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)' }}>
            <h4 style={{ margin: '0 0 10px 0', color: 'var(--gray-800)', fontWeight: 700 }}>Scanning tips:</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-700)', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem', lineHeight: '1.5' }}>
              {(result.recommendations?.preventive || []).map((tip, idx) => (
                <li key={idx}>{tip}</li>
              ))}
            </ul>
          </div>
        </div>
      </motion.div>
    )
  }

  const info = result.disease_info
  const isHealthy = info.is_healthy
  const confidence = result.confidence || 0
  const gsa = result.gsa_metrics || {}
  const healthScore = gsa.plant_health_score ?? 100
  const severityLevel = gsa.severity_level || 'Healthy'
  const affectedAreaPct = gsa.attention_affected_region_percent ?? gsa.affected_area_pct ?? 0
  const treatmentPriority = gsa.treatment_priority || 'No specific chemical intervention needed. Monitor crop health routinely.'
  const rd = result.research_details || {}
  const visuals = rd.visuals || {}

  // Resolve visual assets
  const originalSrc = visuals.original || result._preview
  const heatmapSrc = visuals.heatmap
  const maskSrc = visuals.leaf_mask
  const actMaskSrc = visuals.activation_mask
  const overlaySrc = visuals.overlay

  const tabOptions = [
    { id: 'original', label: 'Original', src: originalSrc },
    { id: 'heatmap', label: 'AI Attention', src: heatmapSrc },
    { id: 'leaf_mask', label: 'Leaf Region', src: maskSrc },
    { id: 'activation_mask', label: 'Affected Activation', src: actMaskSrc },
    { id: 'overlay', label: 'Overlay', src: overlaySrc }
  ]

  // Setup traffic light indicator settings
  let trafficBg = 'var(--green-100)'
  let trafficColor = 'var(--green-700)'
  let trafficDot = '🟢'

  if (!isHealthy) {
    const sev = severityLevel.toLowerCase()
    if (sev === 'mild') {
      trafficBg = 'var(--green-100)'
      trafficColor = 'var(--green-700)'
      trafficDot = '🟢'
    } else if (sev === 'moderate') {
      trafficBg = '#fff8e1'
      trafficColor = 'var(--accent-orange)'
      trafficDot = '🟠'
    } else {
      trafficBg = '#ffebee'
      trafficColor = 'var(--accent-red)'
      trafficDot = '🔴'
    }
  }

  const activeImage = tabOptions.find(t => t.id === activeTab)?.src || originalSrc

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 1. Header with score and prediction */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }} 
        animate={{ opacity: 1, y: 0 }} 
        className="card"
        style={{ padding: '0', overflow: 'hidden', border: `1px solid ${trafficColor}20` }}
      >
        <div style={{ background: trafficBg, padding: '24px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '24px' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>AI ANALYSIS COMPLETE</div>
            <h2 style={{ margin: '4px 0 0', fontSize: '1.6rem', color: 'var(--gray-900)', fontWeight: 800 }}>{result.display_name || info.display_name}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '8px' }}>
              <span style={{ fontSize: '0.9rem', color: 'var(--gray-600)', fontWeight: 600 }}>Confidence: <strong>{confidence.toFixed(1)}%</strong></span>
              <span style={{ fontSize: '0.9rem', color: 'var(--gray-600)', fontWeight: 600 }}>Affected Area: <strong>{affectedAreaPct.toFixed(1)}%</strong></span>
              {(result.illumination_info?.is_illumination_normalized || result.quality_info?.illumination?.is_illumination_normalized) && (
                <span style={{ fontSize: '0.78rem', background: '#e8f5e9', color: '#2e7d32', padding: '3px 10px', borderRadius: '12px', border: '1px solid #c8e6c9', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }} title="Field illumination standardized before segmentation">
                  ☀️ {(result.illumination_info?.lighting_condition || result.quality_info?.illumination?.lighting_condition || 'Standardized').replace(/_/g, ' ')}
                </span>
              )}
            </div>
          </div>
          <HealthScoreGauge score={healthScore} trafficColor={trafficColor} trafficDot={trafficDot} severity={severityLevel} />
        </div>
      </motion.div>

      {/* 2. Visual Explanation (Tabbed interface) */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card" 
        style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '20px', background: '#fff', border: '1px solid var(--gray-200)' }}
      >
        <div>
          <h3 style={{ margin: '0 0 4px', fontSize: '1.15rem', color: 'var(--green-900)', fontWeight: 800 }}>Explainable Spatial Activations</h3>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--gray-500)' }}>Use the controls below to toggle visual segmentation overlays.</p>
        </div>

        {/* Custom Tab Triggers */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', borderBottom: '1px solid var(--gray-200)', paddingBottom: '10px' }}>
          {tabOptions.map((tab) => (
            <button 
              key={tab.id}
              className={`btn btn-sm ${activeTab === tab.id ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setActiveTab(tab.id)}
              disabled={!tab.src}
              style={{ borderRadius: '6px', fontSize: '0.8rem', padding: '6px 12px' }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content image */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', alignItems: 'center' }}>
          <div style={{ 
            position: 'relative', width: '100%', maxWidth: '380px', aspectRatio: '1.2/1', 
            borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--gray-200)', 
            background: '#152119', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' 
          }}>
            <img src={activeImage} alt={activeTab} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
            <div style={{ position: 'absolute', bottom: '8px', left: '8px', background: 'rgba(0,0,0,0.65)', color: '#fff', fontSize: '0.72rem', padding: '4px 10px', borderRadius: '4px', backdropFilter: 'blur(4px)' }}>
              {tabOptions.find(t => t.id === activeTab)?.label} View
            </div>
          </div>
          
          {/* Scientific Info Box */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ background: 'var(--gray-50)', padding: '16px 20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)' }}>
              <h4 style={{ margin: '0 0 6px', color: 'var(--gray-900)', fontSize: '0.88rem', fontWeight: 800 }}>Interpretative Map Layer</h4>
              <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--gray-600)', lineHeight: 1.45 }}>
                {activeTab === 'original' && "Displays the input leaf photo before feature processing and OTSU threshold filters are run."}
                {activeTab === 'heatmap' && "Highlights regions (in hot red/yellow color bands) that generated the strongest gradients in the final model layer."}
                {activeTab === 'leaf_mask' && "Shows the binary OpenCV detected leaf shape, filtering out table, background noise, or shadows."}
                {activeTab === 'activation_mask' && "Outlines pixel activation thresholds that correspond directly with disease-affected surface indices."}
                {activeTab === 'overlay' && "Combines the heatmap with the leaf image to show where the model was focusing on the physical leaf surface."}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px', color: 'var(--gray-500)', fontSize: '0.78rem', alignItems: 'flex-start', paddingLeft: '4px' }}>
              <Info size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>GSA algorithms calculate area percentages based on visual activations inside the leaf boundary, not physical biomass section assays.</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 3. Disease Information / Insights (Expandable sections) */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <DiseaseInsights diseaseInfo={info} />
      </motion.div>

      {/* 4. What Should You Do? (Agronomic Recommendations) */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card" 
        style={{ padding: '32px', background: '#fff', border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', gap: '24px' }}
      >
        <div>
          <h3 style={{ margin: '0 0 6px', fontSize: '1.25rem', color: 'var(--green-900)', fontWeight: 800 }}>What Should You Do?</h3>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--gray-500)' }}>Actionable insights from GreenScan Agronomists.</p>
        </div>

        {/* Immediate Action */}
        <div style={{ background: '#f4fbf6', borderLeft: `4px solid ${trafficColor}`, padding: '16px 20px', borderRadius: '8px' }}>
          <div style={{ fontWeight: 800, fontSize: '0.78rem', color: 'var(--green-900)', letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: '4px' }}>Immediate Action:</div>
          <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--gray-800)', lineHeight: '1.5' }}>{treatmentPriority}</p>
        </div>

        {/* Treatment & Prevention */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
          
          {/* Treatment options */}
          {(result.recommendations?.organic_plan?.length > 0 || result.recommendations?.chemical_plan?.length > 0) && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <h4 style={{ color: 'var(--green-800)', margin: 0, fontSize: '0.95rem', fontWeight: 800 }}>
                💡 Treatment Options
              </h4>
              
              {result.recommendations?.organic_plan?.length > 0 && (
                <div>
                  <h5 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--green-700)', fontWeight: 700 }}>Organic Remedies</h5>
                  <ul style={{ margin: 0, paddingLeft: '18px', color: 'var(--gray-700)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '6px', lineHeight: 1.45 }}>
                    {result.recommendations.organic_plan.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              )}

              {result.recommendations?.chemical_plan?.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <h5 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--accent-orange)', fontWeight: 700 }}>Chemical Treatment</h5>
                  <ul style={{ margin: 0, paddingLeft: '18px', color: 'var(--gray-700)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '6px', lineHeight: 1.45 }}>
                    {result.recommendations.chemical_plan.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Prevention Plan */}
          {result.recommendations?.prevention_plan?.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <h4 style={{ color: 'var(--accent-blue)', margin: 0, fontSize: '0.95rem', fontWeight: 800 }}>
                🛡️ Prevention Strategies
              </h4>
              <ul style={{ margin: 0, paddingLeft: '18px', color: 'var(--gray-700)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '6px', lineHeight: 1.45 }}>
                {result.recommendations.prevention_plan.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}

        </div>
      </motion.div>

    </div>
  )
}
