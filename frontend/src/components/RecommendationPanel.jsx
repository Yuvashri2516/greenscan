import { motion } from 'framer-motion'
import { Leaf, Beaker, Shield, ChevronRight, CheckSquare, Info } from 'lucide-react'
import '../index.css'

export default function RecommendationPanel({ result }) {
  // Safety checks - don't show recommendations if the result is empty, healthy, or unreliable
  if (!result || result.is_reliable === false || !result.disease_info || result.disease_info.is_healthy) return null

  const recs = result.recommendations || {}

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  }

  const PlanSection = ({ title, icon, items, color }) => {
    if (!items || items.length === 0) return null
    return (
      <motion.div variants={fadeInUp} style={{ marginBottom: '24px' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', marginBottom: '12px', fontSize: '1.05rem', fontWeight: 700 }}>
          {icon} {title}
        </h4>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {items.map((item, i) => (
            <motion.li 
              key={i} 
              whileHover={{ x: 4 }}
              style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', background: 'var(--white)', padding: '16px', borderRadius: 'var(--radius-md)', border: `1px solid ${color}20`, boxShadow: 'var(--shadow-sm)' }}
            >
              <ChevronRight size={18} color={color} style={{ marginTop: '2px', flexShrink: 0 }} />
              <span style={{ color: 'var(--gray-700)', fontSize: '0.9rem', lineHeight: '1.5' }}>{item}</span>
            </motion.li>
          ))}
        </ul>
      </motion.div>
    )
  }

  // Action steps derived dynamically
  const actionPlanSteps = [
    "Inspect nearby leaves and plants for similar symptoms to gauge spread rate.",
    ...(recs.prevention_plan ? [recs.prevention_plan[0]] : ["Maintain proper foliage aeration and spacing."]),
    ...(recs.organic_plan ? [recs.organic_plan[0]] : ["Apply preventive organic sprays."]),
    "Monitor the crop daily over the next 3 to 5 days.",
    "Re-scan the leaves if symptoms worsen or expand."
  ].filter(Boolean)

  return (
    <motion.div 
      initial="hidden" 
      animate="visible" 
      variants={staggerContainer}
      className="card" 
      style={{ padding: '32px', background: 'var(--gray-50)', border: '1px solid var(--gray-200)' }}
    >
      <motion.h3 
        variants={fadeInUp} 
        style={{ color: 'var(--green-900)', marginBottom: '24px', fontSize: '1.4rem', borderBottom: '2px solid var(--green-200)', paddingBottom: '12px', fontWeight: 800 }}
      >
        Treatment Recommendations & Action Plan
      </motion.h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '32px' }}>
        {/* Treatment plans columns */}
        <div>
          <PlanSection 
            title="Organic Treatment Solutions" 
            icon={<Leaf size={20} color="var(--green-700)" />} 
            items={recs.organic_plan} 
            color="var(--green-700)" 
          />
          <PlanSection 
            title="Preventive Measures" 
            icon={<Shield size={20} color="var(--accent-blue)" />} 
            items={recs.prevention_plan} 
            color="var(--accent-blue)" 
          />
        </div>

        <div>
          <PlanSection 
            title="Chemical Treatment Solutions" 
            icon={<Beaker size={20} color="var(--accent-orange)" />} 
            items={recs.chemical_plan} 
            color="var(--accent-orange)" 
          />

          {/* Chemical Disclaimer */}
          {recs.chemical_plan?.length > 0 && (
            <motion.div 
              variants={fadeInUp} 
              style={{ display: 'flex', gap: '10px', background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e', padding: '16px', borderRadius: '12px', fontSize: '0.82rem', lineHeight: 1.45 }}
            >
              <Info size={20} style={{ flexShrink: 0 }} />
              <div>
                <strong>Pesticide Safety Warning:</strong> Follow chemical product labels and local agricultural regulatory guidance closely. Observe recommended dosages and harvest wait periods.
              </div>
            </motion.div>
          )}

          {/* What Should You Do Now Action Plan */}
          <motion.div variants={fadeInUp} style={{ marginTop: '24px' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--gray-800)', marginBottom: '12px', fontSize: '1.05rem', fontWeight: 700 }}>
              <CheckSquare size={20} color="var(--green-800)" /> What Should You Do Now?
            </h4>
            <div style={{ background: '#ffffff', border: '1px solid var(--gray-200)', borderRadius: '12px', padding: '20px' }}>
              <ol style={{ paddingLeft: '20px', margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.88rem', color: 'var(--gray-700)', lineHeight: '1.5' }}>
                {actionPlanSteps.map((step, idx) => (
                  <li key={idx}>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
