import React, { useState } from 'react'
import { Info, Eye, BarChart2, Shield } from 'lucide-react'
import '../index.css'

export default function GradCAMPanel({ result }) {
  const [activeTab, setActiveTab] = useState('overlay')
  const [showAdvancedStats, setShowAdvancedStats] = useState(false)

  const rd = result?.research_details
  const visuals = rd?.visuals || {}
  
  const heatmapSrc = visuals.heatmap
  const originalSrc = visuals.original || result?._preview
  const maskSrc = visuals.leaf_mask
  const actMaskSrc = visuals.activation_mask
  const overlaySrc = visuals.overlay

  // Render nothing if no visuals are available
  if (!originalSrc && !heatmapSrc) return null

  const getImageSrc = () => {
    switch (activeTab) {
      case 'heatmap': return heatmapSrc || originalSrc
      case 'leaf_mask': return maskSrc || originalSrc
      case 'activation_mask': return actMaskSrc || originalSrc
      case 'overlay': return overlaySrc || originalSrc
      case 'original':
      default: return originalSrc
    }
  }

  const tabLabels = {
    original: 'Original Leaf',
    heatmap: 'Grad-CAM Heatmap',
    overlay: 'Activation Overlay',
    leaf_mask: 'Leaf Contour Mask',
    activation_mask: 'Spatial Activation Mask'
  }

  return (
    <div className="card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Title */}
      <div>
        <h3 style={{ margin: '0 0 6px', fontSize: '1.4rem', color: 'var(--green-900)', fontWeight: 800 }}>
          Why did GreenScan predict this?
        </h3>
        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--gray-600)' }}>
          Visualizing internal neural network activations influencing the AI's diagnosis.
        </p>
      </div>

      {/* Toggles Row */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', borderBottom: '1px solid var(--gray-200)', paddingBottom: '12px' }}>
        {['original', 'heatmap', 'overlay'].map((tab) => (
          <button 
            key={tab}
            className={`btn btn-sm ${activeTab === tab ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveTab(tab)}
            style={{ borderRadius: '8px', fontSize: '0.85rem' }}
          >
            {tabLabels[tab]}
          </button>
        ))}

        <button
          className={`btn btn-sm ${['leaf_mask', 'activation_mask'].includes(activeTab) ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => setActiveTab('activation_mask')}
          style={{ borderRadius: '8px', fontSize: '0.85rem' }}
        >
          🔬 Research Masks
        </button>

        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setShowAdvancedStats(!showAdvancedStats)}
          style={{ marginLeft: 'auto', borderRadius: '8px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px' }}
        >
          <BarChart2 size={14} /> {showAdvancedStats ? 'Hide Pixel Stats' : 'Show Pixel Stats'}
        </button>
      </div>

      {/* Sub-tab selection for Advanced Research Masks if chosen */}
      {['leaf_mask', 'activation_mask'].includes(activeTab) && (
        <div style={{ display: 'flex', gap: '8px', marginTop: '-8px' }}>
          {['leaf_mask', 'activation_mask'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: activeTab === tab ? 'var(--green-100)' : 'transparent',
                color: activeTab === tab ? 'var(--green-800)' : 'var(--gray-600)',
                border: 'none', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer'
              }}
            >
              {tabLabels[tab]}
            </button>
          ))}
        </div>
      )}

      {/* Main Visual Display */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', alignItems: 'start' }}>
        <div style={{ 
          position: 'relative', 
          borderRadius: '16px', 
          overflow: 'hidden',
          border: '1px solid var(--gray-200)',
          aspectRatio: '1.2/1',
          background: '#1a1a1a',
          boxShadow: 'var(--shadow-sm)',
          maxWidth: '540px',
          margin: '0 auto',
          width: '100%'
        }}>
          <img 
            src={getImageSrc()} 
            alt={tabLabels[activeTab]} 
            style={{ 
              width: '100%', 
              height: '100%', 
              objectFit: 'contain',
              display: 'block'
            }} 
          />
          <div style={{
            position: 'absolute', bottom: '12px', left: '12px',
            background: 'rgba(0,0,0,0.65)', color: '#fff', fontSize: '0.75rem',
            padding: '6px 12px', borderRadius: '6px', backdropFilter: 'blur(4px)',
            fontWeight: 600
          }}>
            {tabLabels[activeTab]}
          </div>
        </div>

        {/* Scientific Disclosures */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div className="alert alert-info" style={{ background: 'var(--green-50)', border: '1px solid var(--green-200)', color: 'var(--green-800)', padding: '16px' }}>
            <Info size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: '0.88rem', lineHeight: '1.5' }}>
              <p style={{ margin: '0 0 6px' }}>
                <strong>How it works:</strong> Highlighted regions show areas that received stronger attention from the AI model while making its prediction.
              </p>
              <p style={{ margin: 0, fontSize: '0.82rem', opacity: 0.9 }}>
                ⚠️ <em>Scientific disclaimer:</em> These highlighted regions represent model attention and should not be interpreted as exact disease boundaries.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Research Stats Block */}
      {showAdvancedStats && rd && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', 
          gap: '12px', 
          background: 'var(--gray-50)', 
          padding: '20px', 
          borderRadius: '12px', 
          border: '1px solid var(--gray-200)',
          fontSize: '0.85rem'
        }}>
          <div><strong>Total Leaf Pixels:</strong> {rd.leaf_pixels.toLocaleString()}</div>
          <div><strong>Activated Heatmap Pixels:</strong> {rd.activated_pixels.toLocaleString()}</div>
          <div><strong>Estimated Attention Area:</strong> {rd.attention_affected_region_percent}%</div>
          <div><strong>Grad-CAM Threshold:</strong> {rd.threshold_used}</div>
          <div><strong>Mean Leaf Activation:</strong> {rd.mean_leaf_activation}</div>
          <div><strong>Mean Activated intensity:</strong> {rd.mean_activated_activation}</div>
        </div>
      )}
    </div>
  )
}
