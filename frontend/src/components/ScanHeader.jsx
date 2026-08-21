import { motion } from 'framer-motion';
import '../index.css';

export default function ScanHeader() {
  return (
    <motion.section
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="scan-header"
      style={{
        textAlign: 'center',
        padding: 'var(--sp-12) var(--sp-6)',
        background: 'linear-gradient(135deg, var(--green-200), var(--green-50))',
        position: 'relative',
        overflow: 'hidden',
        marginBottom: 'var(--sp-8)'
      }}
    >
      {/* Subtle floating leaves animation */}
      <div className="leaf-animation" />
      <h1 style={{ fontSize: '2.4rem', color: 'var(--green-900)', fontWeight: 800, marginBottom: 'var(--sp-4)' }}>
        AI Plant Health Scanner
      </h1>
      <p style={{ fontSize: '1rem', color: 'var(--gray-700)', maxWidth: '720px', margin: '0 auto' }}>
        Upload a clear tomato leaf image and let GreenScan analyze its health using explainable artificial intelligence.
      </p>
    </motion.section>
  );
}
