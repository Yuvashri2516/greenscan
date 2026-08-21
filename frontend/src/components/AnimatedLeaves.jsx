import React from 'react';
import { motion } from 'framer-motion';

// SVG leaf path (simple leaf shape)
const LeafSVG = ({ size = 24, color = 'var(--green-400)' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={color}
    xmlns="http://www.w3.org/2000/svg"
    style={{ display: 'block' }}
  >
    <path d="M12 2C10 5 6 8 6 12c0 3.31 2.69 6 6 6s6-2.69 6-6c0-4-4-7-6-10z" />
  </svg>
);

/**
 * AnimatedLeaves renders a collection of floating leaf SVGs that drift across the screen.
 * The component accepts an optional `className` to position it (e.g., background or foreground).
 */
const AnimatedLeaves = ({ className = '' }) => {
  // Generate a random set of leaves
  const leaves = Array.from({ length: 12 }).map((_, i) => {
    const delay = Math.random() * 5; // seconds
    const duration = 8 + Math.random() * 4; // seconds
    const size = 12 + Math.random() * 20; // px
    const startX = Math.random() * 100; // percent
    const endX = startX + (Math.random() * 20 - 10); // slight horizontal drift
    const startY = 100; // start from bottom
    const endY = -20; // end above top
    const opacity = 0.3 + Math.random() * 0.5;
    const rotate = Math.random() * 360;
    const scale = 0.5 + Math.random() * 0.7;
    return (
      <motion.div
        key={i}
        initial={{ x: `${startX}%`, y: `${startY}%`, opacity: 0, rotate: 0, scale: 0.8 }}
        animate={{
          x: `${endX}%`,
          y: `${endY}%`,
          opacity: [0, opacity, 0],
          rotate: [0, rotate, rotate],
          scale,
        }}
        transition={{
          delay,
          duration,
          repeat: Infinity,
          repeatType: 'loop',
          ease: 'linear',
        }}
        style={{
          position: 'absolute',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      >
        <LeafSVG size={size} />
      </motion.div>
    );
  });

  return <div className={className} style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>{leaves}</div>;
};

export default AnimatedLeaves;
