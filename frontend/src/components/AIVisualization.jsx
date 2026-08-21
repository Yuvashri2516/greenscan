import { motion } from 'framer-motion'
import '../index.css'

export default function AIVisualization() {
  // Preset scanning node coordinates over the leaf layout
  const nodes = [
    { top: '25%', left: '42%', delay: 0.1 },
    { top: '35%', left: '60%', delay: 0.4 },
    { top: '50%', left: '30%', delay: 0.2 },
    { top: '55%', left: '50%', delay: 0.6 },
    { top: '65%', left: '72%', delay: 0.3 },
    { top: '45%', left: '48%', delay: 0.5 },
    { top: '75%', left: '38%', delay: 0.7 }
  ]

  return (
    <div 
      style={{ 
        position: 'relative', 
        width: '100%', 
        maxWidth: '440px', 
        aspectRatio: '1/1',
        borderRadius: 'var(--radius-xl)',
        background: '#152119', // Sleek dark canvas background
        border: '1px solid rgba(76, 175, 80, 0.2)',
        boxShadow: '0 24px 50px rgba(10, 34, 16, 0.15)',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px'
      }}
    >
      {/* Background Computer Vision Radar Grid */}
      <div 
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.08,
          backgroundSize: '24px 24px',
          backgroundImage: `
            linear-gradient(to right, #4caf50 1px, transparent 1px),
            linear-gradient(to bottom, #4caf50 1px, transparent 1px)
          `,
          pointerEvents: 'none'
        }}
      />

      {/* Target Crosshairs */}
      <div style={{ position: 'absolute', top: '15px', left: '15px', width: '12px', height: '12px', borderLeft: '2px solid rgba(76,175,80,0.6)', borderTop: '2px solid rgba(76,175,80,0.6)' }} />
      <div style={{ position: 'absolute', top: '15px', right: '15px', width: '12px', height: '12px', borderRight: '2px solid rgba(76,175,80,0.6)', borderTop: '2px solid rgba(76,175,80,0.6)' }} />
      <div style={{ position: 'absolute', bottom: '15px', left: '15px', width: '12px', height: '12px', borderLeft: '2px solid rgba(76,175,80,0.6)', borderBottom: '2px solid rgba(76,175,80,0.6)' }} />
      <div style={{ position: 'absolute', bottom: '15px', right: '15px', width: '12px', height: '12px', borderRight: '2px solid rgba(76,175,80,0.6)', borderBottom: '2px solid rgba(76,175,80,0.6)' }} />

      {/* Scientific Overlay Texts */}
      <div style={{ position: 'absolute', top: '15px', left: '35px', fontSize: '0.68rem', fontFamily: 'monospace', color: 'rgba(76, 175, 80, 0.7)', letterSpacing: '0.05em' }}>
        SYS: EFFICIENTNET_B0 // ACTIVE
      </div>
      <div style={{ position: 'absolute', bottom: '15px', right: '35px', fontSize: '0.68rem', fontFamily: 'monospace', color: 'rgba(76, 175, 80, 0.7)', letterSpacing: '0.05em' }}>
        GSA_METRICS: CALIBRATING...
      </div>

      {/* Main Tomato Leaf Image Wrapper */}
      <div style={{ position: 'relative', width: '90%', height: '90%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {/* Glowing Leaf Outline */}
        <div 
          style={{
            position: 'absolute',
            inset: '-5px',
            borderRadius: '50%',
            border: '2px dashed rgba(76, 175, 80, 0.15)',
            animation: 'spin 40s linear infinite',
            pointerEvents: 'none'
          }}
        />

        {/* Botanical Visual Leaf */}
        <img 
          src="/assets/hero_plant.png" 
          alt="Tomato Leaf Diagnostics Visualization"
          onError={(e) => {
            e.target.src = "https://images.unsplash.com/photo-1592417817098-8f3d6eb19675?auto=format&fit=crop&w=600&q=80"
          }}
          style={{
            width: '85%',
            height: '85%',
            objectFit: 'contain',
            borderRadius: '12px',
            opacity: 0.85,
            filter: 'contrast(1.05) brightness(0.95)'
          }}
        />

        {/* Dynamic Scanning Line */}
        <motion.div 
          animate={{ y: ['-10%', '110%', '-10%'] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute',
            left: '5%',
            right: '5%',
            height: '3px',
            background: 'linear-gradient(90deg, transparent, #4caf50, transparent)',
            boxShadow: '0 0 12px 1px #4caf50',
            zIndex: 4,
            pointerEvents: 'none'
          }}
        />

        {/* Detection Nodes/Nodes mapping */}
        {nodes.map((node, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0.2, scale: 0.8 }}
            animate={{ 
              opacity: [0.3, 0.9, 0.3], 
              scale: [0.9, 1.2, 0.9] 
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              delay: node.delay, 
              ease: 'easeInOut' 
            }}
            style={{
              position: 'absolute',
              top: node.top,
              left: node.left,
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#4caf50',
              boxShadow: '0 0 8px 2px #4caf50',
              zIndex: 3,
              pointerEvents: 'none'
            }}
          />
        ))}

        {/* Intersecting mapping lines between nodes (computer vision feel) */}
        <svg 
          style={{ 
            position: 'absolute', 
            inset: 0, 
            width: '100%', 
            height: '100%', 
            zIndex: 2, 
            pointerEvents: 'none',
            opacity: 0.25 
          }}
        >
          <line x1="42%" y1="25%" x2="48%" y2="45%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="48%" y1="45%" x2="60%" y2="35%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="30%" y1="50%" x2="48%" y2="45%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="50%" y1="55%" x2="48%" y2="45%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="50%" y1="55%" x2="72%" y2="65%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="38%" y1="75%" x2="50%" y2="55%" stroke="#4caf50" strokeWidth="1" strokeDasharray="3 3" />
        </svg>

      </div>
    </div>
  )
}
