import { motion } from 'framer-motion'
import { Leaf, Info, ShieldCheck, Eye, Cpu, BookOpen } from 'lucide-react'
import '../index.css'

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } }
}

export default function AboutPage() {
  return (
    <motion.div 
      initial="hidden" 
      animate="visible" 
      variants={staggerContainer}
      style={{ minHeight: '100vh', background: 'var(--green-50)', padding: '60px 0 100px' }}
    >
      <div className="container" style={{ maxWidth: '850px' }}>
        
        {/* Page Title */}
        <motion.div variants={fadeInUp} style={{ textAlign: 'center', marginBottom: '60px' }}>
          <div className="section-label">Research & Science</div>
          <h1 style={{ color: 'var(--green-900)', fontSize: '2.8rem', fontWeight: 800 }}>About GreenScan</h1>
          <p style={{ color: 'var(--gray-600)', fontSize: '1.15rem', marginTop: '12px', lineHeight: 1.6 }}>
            A research-grade agricultural decision support platform bridging explainable deep learning with field operations.
          </p>
        </motion.div>

        {/* Sections Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
          
          {/* Mission */}
          <motion.div variants={fadeInUp} className="card" style={{ padding: '36px', background: '#fff', border: '1px solid var(--gray-200)' }}>
            <h3 style={{ color: 'var(--green-900)', fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700 }}>
              <Leaf size={22} color="var(--green-700)" /> Platform Mission
            </h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: '1.7', fontSize: '0.95rem', margin: 0 }}>
              Tomato crops are vulnerable to devastating pathogens like Early Blight and Late Blight. Traditional diagnosis relies heavily on expert inspections or delayed lab analysis. GreenScan's mission is to deliver fast, explainable, and scientifically validated agricultural AI diagnostic maps directly to farmers and researchers, enabling early containment actions and reducing crop losses globally.
            </p>
          </motion.div>

          {/* Technology */}
          <motion.div variants={fadeInUp} className="card" style={{ padding: '36px', background: '#fff', border: '1px solid var(--gray-200)' }}>
            <h3 style={{ color: 'var(--green-900)', fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700 }}>
              <Cpu size={22} color="var(--green-700)" /> Core Deep Learning Technology
            </h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: '1.7', fontSize: '0.95rem', marginBottom: '16px' }}>
              GreenScan integrates a highly optimized deep learning pipeline designed to achieve high classification accuracies on mobile edge and web environments:
            </p>
            <ul style={{ paddingLeft: '20px', color: 'var(--gray-700)', fontSize: '0.92rem', display: 'flex', flexDirection: 'column', gap: '10px', lineHeight: 1.5 }}>
              <li><strong>EfficientNet-B0 Backbone:</strong> A convolutional neural network scaled using compound coefficient sizing, achieving top-tier feature map abstractions with reduced parameters.</li>
              <li><strong>FastAPI Endpoint Gateway:</strong> High-performance server gateway hosting the compiled TensorFlow models for sub-second network inference latencies.</li>
              <li><strong>Local Data Logger:</strong> Historically saves diagnostic entries using an SQLite logging model to track localized disease distributions.</li>
            </ul>
          </motion.div>

          {/* Explainable AI */}
          <motion.div variants={fadeInUp} className="card" style={{ padding: '36px', background: '#fff', border: '1px solid var(--gray-200)' }}>
            <h3 style={{ color: 'var(--green-900)', fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700 }}>
              <Eye size={22} color="var(--green-700)" /> Explainable AI (XAI)
            </h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: '1.7', fontSize: '0.95rem', margin: 0 }}>
              AI models are often perceived as black boxes, making trust difficult to establish in critical farming diagnostics. GreenScan implements <strong>Gradient-weighted Class Activation Mapping (Grad-CAM)</strong>. By computing gradients at the final convolutional layer, GreenScan overlays visual heatmaps indicating which leaf pixels the AI model focused on during classification. This allows users to scientifically verify that the network is looking at actual disease patterns rather than background dirt or shadows.
            </p>
          </motion.div>

          {/* Farmer-Centric Design */}
          <motion.div variants={fadeInUp} className="card" style={{ padding: '36px', background: '#fff', border: '1px solid var(--gray-200)' }}>
            <h3 style={{ color: 'var(--green-900)', fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700 }}>
              <Info size={22} color="var(--green-700)" /> Farmer-Centric Information Design
            </h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: '1.7', fontSize: '0.95rem', margin: 0 }}>
              We convert complex scientific matrices into clear, actionable advice. Using our custom <strong>GreenScan Severity Analyzer (GSA)</strong>, the system interprets spatial activation vectors to output a simplified 0-100 Plant Health Score and severity level (Healthy, Mild, Moderate, Severe). This translates model parameters into specific chemical, organic, and preventative cultivation guides that farmers can easily apply in the fields.
            </p>
          </motion.div>

          {/* Research & Validation */}
          <motion.div variants={fadeInUp} className="card" style={{ padding: '36px', background: '#fff', border: '1px solid var(--gray-200)' }}>
            <h3 style={{ color: 'var(--green-900)', fontSize: '1.35rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 700 }}>
              <ShieldCheck size={22} color="var(--green-700)" /> Research & Expert Validation
            </h3>
            <p style={{ color: 'var(--gray-700)', lineHeight: '1.7', fontSize: '0.95rem', margin: 0 }}>
              GreenScan is a research-supported diagnostic platform. The AI model is validated against expert-annotated plant pathology data. Please note that GreenScan serves as a decision support system; it provides mathematical pattern probabilities and should not be used as a final legal diagnostic replacement for professional agricultural expert evaluations.
            </p>
          </motion.div>

        </div>

      </div>
    </motion.div>
  )
}
