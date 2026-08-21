import React from 'react';
import { Leaf, Cpu, Activity, ShieldCheck } from 'lucide-react';

// Define a set of feature items for the landing page
const features = [
  {
    icon: <Leaf size={24} className="text-green-600" />, // Note: lucide-react icons are components, using JSX directly works in render
    title: 'AI‑Powered Diagnosis',
    description: 'Fast, accurate disease detection using EfficientNet‑B0.'
  },
  {
    icon: <Cpu size={24} className="text-green-600" />,
    title: 'Explainable Grad‑CAM',
    description: 'Visual activation maps show exactly why a prediction was made.'
  },
  {
    icon: <Activity size={24} className="text-green-600" />,
    title: 'Plant Health Score',
    description: 'Quantified severity index and actionable treatment advice.'
  },
  {
    icon: <ShieldCheck size={24} className="text-green-600" />,
    title: 'Farmer‑Friendly',
    description: 'Clear recommendations, multilingual support, and chatbot help.'
  }
];

export default function FeaturesSection() {
  return (
    <section
      className="glass-card"
      style={{
        background: '#fff',
        padding: '80px 20px',
        borderBottom: '1px solid var(--gray-200)'
      }}
    >
      <div className="container" style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h2 style={{ color: 'var(--green-900)', fontSize: '2.5rem', fontWeight: 800, fontFamily: 'var(--font-serif)' }}>
          Why GreenScan?
        </h2>
        <p style={{ color: 'var(--gray-600)', fontSize: '1rem', maxWidth: '560px', margin: '0 auto' }}>
          A premium AI‑driven platform that brings research‑grade diagnostics to every farmer.
        </p>
      </div>
      <div
        className="features-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '30px',
          maxWidth: '1200px',
          margin: '0 auto'
        }}
      >
        {features.map((f, idx) => (
          <div
            key={idx}
            className="feature-card"
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(8px)',
              borderRadius: '16px',
              border: '1px solid var(--gray-200)',
              padding: '24px',
              textAlign: 'center',
              boxShadow: '0 8px 24px rgba(10,34,16,0.04)'
            }}
          >
            <div style={{ marginBottom: '12px' }}>{f.icon}</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--gray-900)', marginBottom: '8px' }}>
              {f.title}
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--gray-600)' }}>{f.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
