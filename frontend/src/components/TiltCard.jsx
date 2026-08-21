import { useState, useRef } from 'react'

/**
 * TiltCard component provides a premium, GPU-accelerated 3D tilt interaction on hover.
 * Uses vanilla React state and mouse position monitoring to apply perspective rotation.
 */
export default function TiltCard({ children, className = '', style = {}, maxRotation = 10 }) {
  const cardRef = useRef(null)
  const [transform, setTransform] = useState('')
  const [glareStyle, setGlareStyle] = useState({ opacity: 0 })

  const handleMouseMove = (e) => {
    const card = cardRef.current
    if (!card) return

    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    // Calculate mouse position relative to center of the card (-0.5 to 0.5)
    const normalizedX = (x / rect.width) - 0.5
    const normalizedY = (y / rect.height) - 0.5

    // Calculate rotation angles (X rotation handles Y tilt, Y rotation handles X tilt)
    const rotateX = -(normalizedY * maxRotation).toFixed(2)
    const rotateY = (normalizedX * maxRotation).toFixed(2)

    setTransform(`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`)

    // Position gradient glare based on current mouse coordinates
    const glareX = (x / rect.width) * 100
    const glareY = (y / rect.height) * 100
    setGlareStyle({
      opacity: 0.35,
      background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,255,255,0.2) 0%, transparent 60%)`,
    })
  }

  const handleMouseLeave = () => {
    // Reset element transformations smoothly
    setTransform('perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)')
    setGlareStyle({ opacity: 0, transition: 'opacity 0.4s ease' })
  }

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`tilt-card-wrapper ${className}`}
      style={{
        position: 'relative',
        transition: 'transform 0.15s cubic-bezier(0.25, 0.61, 0.355, 1)',
        transform,
        transformStyle: 'preserve-3d',
        ...style
      }}
    >
      {/* Glare Sheen Overlay Layer */}
      <div 
        style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          pointerEvents: 'none',
          zIndex: 5,
          borderRadius: 'inherit',
          ...glareStyle
        }}
      />
      {children}
    </div>
  )
}
