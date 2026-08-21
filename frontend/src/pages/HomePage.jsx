import { useRef, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Leaf, Cpu, Activity, CheckCircle2, ShieldCheck } from 'lucide-react'
import AnimatedLeaves from '../components/AnimatedLeaves.jsx'
import FeaturesSection from '../components/FeaturesSection.jsx'

import AIVisualization from '../components/AIVisualization.jsx'
import '../index.css'

const fadeInUp = {
  hidden: { opacity: 0, y: 35 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } }
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } }
}

function HeroMockup() {
  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '360px', margin: '0 auto' }}>
      {/* Device Shell Frame */}
      <div 
        style={{
          width: '100%',
          aspectRatio: '1/1.9',
          background: '#0a2210',
          borderRadius: '40px',
          padding: '12px',
          boxShadow: '0 30px 60px rgba(10,34,16,0.18)',
          border: '4px solid #1b4e28',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Notch */}
        <div style={{ position: 'absolute', top: '10px', left: '50%', transform: 'translateX(-50%)', width: '80px', height: '16px', background: '#000', borderRadius: '8px', zIndex: 10 }} />
        
        {/* Screen Display */}
        <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: '28px', overflow: 'hidden' }}>
          <img 
            src="/assets/hero_plant.png" 
            alt="Leaf Scan Diagnostics" 
            style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
          />
          
          {/* Scan Active Indicator HUD Overlay */}
          <div style={{ position: 'absolute', inset: 0, border: '1.5px dashed rgba(255,255,255,0.4)', borderRadius: '28px', margin: '10px', pointerEvents: 'none' }} />

          {/* AI Result Card */}
          <div style={{ position: 'absolute', bottom: '12px', left: '12px', right: '12px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(8px)', padding: '12px 14px', borderRadius: '16px', border: '1px solid rgba(76,175,80,0.15)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
              <span style={{ fontSize: '0.62rem', fontWeight: 800, color: 'var(--green-700)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>CLASSIFIER ACTIVE</span>
              <span style={{ fontSize: '0.62rem', fontWeight: 800, background: 'var(--green-100)', color: 'var(--green-800)', padding: '1px 5px', borderRadius: '4px' }}>98.2%</span>
            </div>
            <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--gray-900)' }}>Tomato Early Blight</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--gray-500)' }}>Alternaria solani pathology</div>
          </div>
        </div>
      </div>

      {/* Floating Badge 1: Severity Score */}
      <motion.div 
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          position: 'absolute',
          top: '22%',
          left: '-24px',
          background: '#fff',
          padding: '10px 14px',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(10,34,16,0.06)',
          border: '1px solid var(--gray-200)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          zIndex: 5
        }}
      >
        <span style={{ fontSize: '1rem' }}>📈</span>
        <div>
          <div style={{ fontSize: '0.6rem', color: 'var(--gray-400)', fontWeight: 800, textTransform: 'uppercase' }}>Severity Index</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-orange)' }}>Moderate infection</div>
        </div>
      </motion.div>

      {/* Floating Badge 2: Care Action */}
      <motion.div 
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        style={{
          position: 'absolute',
          bottom: '24%',
          right: '-24px',
          background: '#fff',
          padding: '10px 14px',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(10,34,16,0.06)',
          border: '1px solid var(--gray-200)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          zIndex: 5
        }}
      >
        <span style={{ fontSize: '1rem' }}>🛡️</span>
        <div>
          <div style={{ fontSize: '0.6rem', color: 'var(--gray-400)', fontWeight: 800, textTransform: 'uppercase' }}>PHS Score</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--green-800)' }}>76 / 100 Health</div>
        </div>
      </motion.div>
    </div>
  )
}

function HeroSection() {
  const heroRef = useRef(null)
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const disableParallax = prefersReduced || isMobile

  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"]
  })

  // Smooth scroll transformations
  const yBg = useTransform(scrollYProgress, [0, 1], [0, 60])
  const yContent = useTransform(scrollYProgress, [0, 1], [0, 0])
  const yMockup = useTransform(scrollYProgress, [0, 1], [0, 100])

  return (
    <div 
      ref={heroRef}
      style={{ 
        position: 'relative', 
        overflow: 'hidden', 
        background: '#FAF9F6', // Lighter and warmer off-white background
        padding: '110px 20px 80px',
        minHeight: '85vh',
        display: 'flex',
        alignItems: 'center'
      }}
      className="tech-grid-pattern"
    >
      {/* Soft Greenish Parallax Blur Blob */}
      <motion.div 
        style={{ 
          ...(disableParallax ? {} : { y: yBg }),
          position: 'absolute', top: '5%', left: '8%', width: '450px', height: '450px', 
          background: 'rgba(76, 175, 80, 0.06)', borderRadius: '50%', filter: 'blur(110px)', 
          zIndex: 0 
        }} 
      />
      {/* Animated floating leaves background */}
      <AnimatedLeaves className="hero-leaves" />

      <div className="container" style={{ position: 'relative', zIndex: 5, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '50px' }}>
        
        {/* Left Column: Heading and description */}
        <motion.div 
          style={{ 
            ...(disableParallax ? {} : { y: yContent }),
            flex: '1 1 500px', maxWidth: '620px' 
          }}
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
        >
          <motion.div 
            variants={fadeInUp} 
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '6px', 
              padding: '6px 14px', 
              background: 'var(--green-100)', 
              borderRadius: '9999px', 
              color: 'var(--green-800)', 
              fontWeight: 700, 
              fontSize: '0.78rem', 
              marginBottom: '20px',
              border: '1px solid var(--green-200)'
            }}
          >
            <ShieldCheck size={14} /> AGRONOMIC COMPUTER VISION GATEWAY
          </motion.div>
          
          <motion.h1
              variants={fadeInUp}
              style={{
                fontSize: 'clamp(2.8rem, 6vw, 4rem)',
                color: 'var(--gray-900)',
                marginBottom: '24px',
                letterSpacing: '-0.04em',
                lineHeight: 1.1,
                fontWeight: 800,
                fontFamily: 'var(--font-serif)'
              }}
            >
              GREENSCAN
            </motion.h1>
            <motion.p
              variants={fadeInUp}
              style={{
                fontSize: '1.2rem',
                color: 'var(--gray-700)',
                marginBottom: '32px',
                lineHeight: '1.6',
                maxWidth: '560px'
              }}
            >
              AI‑Powered Plant Health Intelligence – Analyze tomato leaf health with explainable artificial intelligence, visual disease analysis, and farmer‑friendly recommendations.
            </motion.p>
            
            <motion.div variants={fadeInUp} style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
              <Link to="/scan" className="btn btn-primary btn-lg" style={{ textDecoration: 'none', padding: '14px 30px' }} aria-label="Start Scanning">
                Start Scanning
              </Link>
              <Link to="/about" className="btn btn-secondary btn-lg" style={{ textDecoration: 'none', padding: '14px 30px' }} aria-label="Explore GreenScan">
                Explore GreenScan
              </Link>
            </motion.div>
        </motion.div>

        {/* Right Column: Editorial Device Mockup */}
        <motion.div 
          style={{ 
            ...(disableParallax ? {} : { y: yMockup }),
            flex: '1 1 400px', display: 'flex', justifyContent: 'center', position: 'relative' 
          }}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <HeroMockup />
        </motion.div>
      </div>
    </div>
  )
}

function TrustSection() {
  const items = [
    { title: "AI Disease Detection", desc: "Feature map classification" },
    { title: "EfficientNet-B0", desc: "Convolutional backbone model" },
    { title: "Grad-CAM Explainability", desc: "Visual spatial activation maps" },
    { title: "Plant Health Score", desc: "Computed GSA severity metrics" },
    { title: "Farmer-Friendly Results", desc: "Clear agricultural advice" }
  ]

  return (
    <div className="dark-glass-card" style={{ background: '#0e2416', borderTop: '1px solid rgba(255, 255, 255, 0.08)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', padding: '32px 20px', position: 'relative', zIndex: 10 }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '24px' }}>
        {items.map((item, idx) => (
          <div key={idx} style={{ flex: '1 1 180px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} color="var(--green-400)" /> {item.title}
            </span>
            <span style={{ fontSize: '0.82rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: 1.4 }}>{item.desc}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function HowItWorksSection() {
  const steps = [
    { num: '01', title: 'Upload Leaf', desc: 'Select or capture a tomato leaf image on your device.' },
    { num: '02', title: 'AI Detection', desc: 'EfficientNet‑B0 processes the image and predicts disease probabilities.' },
    { num: '03', title: 'Explainable Analysis', desc: 'Grad‑CAM visualises the regions influencing the prediction.' },
    { num: '04', title: 'Health Assessment', desc: 'The GSA engine computes a plant‑health score and severity index.' },
    { num: '05', title: 'Farmer Guidance', desc: 'Tailored treatment recommendations and preventive advice are presented.' }
  ];

  return (
    <div className="glass-card" id="how-it-works" 
      style={{ 
        position: 'relative', 
        padding: '100px 20px', 
        borderBottom: '1px solid var(--gray-200)',
        overflow: 'hidden'
      }}
    >
      {/* Luminous watermarked backdrop */}
      <div 
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'url("/assets/how_it_works_bg.jpg")',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'brightness(2.9) contrast(0.6) saturate(0.9)',
          opacity: 0.68,
          zIndex: 0
        }}
      />
      
      {/* Background color gradient overlay */}
      <div 
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(135deg, #FAF9F6 0%, #f1f8e9 100%)',
          opacity: 0.45,
          zIndex: 1
        }}
      />

      <div className="container" style={{ position: 'relative', zIndex: 2, display: 'flex', flexWrap: 'wrap', gap: '50px', alignItems: 'center' }}>
        
        {/* Left Column: Testimonial/Steps List */}
        <div style={{ flex: '1 1 500px', maxWidth: '600px' }}>
          <div className="section-label" style={{ marginBottom: '12px' }}>Farming Pipeline</div>
          <h2 style={{ color: 'var(--green-900)', fontSize: '2.5rem', fontWeight: 800, marginBottom: '24px', fontFamily: 'var(--font-serif)' }}>
            From Visual Symptoms <br />to Targeted Protection.
          </h2>
          <p style={{ color: 'var(--gray-600)', marginBottom: '40px', fontSize: '1.05rem', lineHeight: 1.6 }}>
            GreenScan combines computer vision models with agricultural database treatment checks to manage crop health in five phases.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
            {steps.map((s, idx) => (
              <div 
                key={idx} 
                style={{ 
                  display: 'flex', 
                  gap: '24px', 
                  borderBottom: idx === steps.length - 1 ? 'none' : '1px solid rgba(10,34,16,0.06)', 
                  paddingBottom: idx === steps.length - 1 ? 0 : '24px' 
                }}
              >
                <span style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--green-700)', marginTop: '4px', letterSpacing: '0.04em' }}>
                  PHASE {s.num}
                </span>
                <div>
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--gray-900)', marginBottom: '6px', fontWeight: 700, fontFamily: 'var(--font-serif)' }}>
                    {s.title}
                  </h3>
                  <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: 1.5, margin: 0 }}>
                    {s.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Device Active Scan Visualizer */}
        <div style={{ flex: '1 1 400px', display: 'flex', justifyContent: 'center' }}>
          <motion.div 
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              position: 'relative',
              width: '100%',
              maxWidth: '380px',
              padding: '16px',
              background: '#0d2214', // dark forest case matching visual styling
              borderRadius: '38px',
              boxShadow: '0 30px 60px rgba(10, 34, 16, 0.18)',
              border: '4px solid #1b4e28'
            }}
          >
            {/* Phone speaker notch */}
            <div style={{ width: '80px', height: '18px', background: '#1b4e28', borderRadius: '10px', margin: '0 auto 12px' }} />
            
            {/* Inside active radar scan visualizer */}
            <AIVisualization />
          </motion.div>
        </div>

      </div>
    </div>
  )
}

function TechnologyPipeline() {
  const technologies = [
      { 
        name: "EfficientNet‑B0",
        desc: "Identifies patterns associated with tomato leaf diseases using a lightweight CNN backbone."
      },
      { 
        name: "Grad‑CAM",
        desc: "Highlights image regions that contributed most to the AI prediction, providing visual explainability."
      },
      { 
        name: "Leaf Segmentation",
        desc: "Separates the leaf from background to focus analysis on the relevant tissue."
      },
      { 
        name: "GreenScan Severity Analyzer (GSA)",
        desc: "Transforms spatial activation into an interpretable plant‑health score and severity index."
      }
    ];

  return (
    <div id="plant-health" className="glass-card" style={{ padding: '95px 20px', background: '#fff', borderBottom: '1px solid var(--gray-200)' }}>
      <div className="container">
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '50px', alignItems: 'center' }}>
          
          {/* Left Column: Leaf active hotspots card */}
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div 
              style={{ 
                position: 'relative', width: '100%', maxWidth: '440px', aspectRatio: '1.25/1', 
                borderRadius: '24px', overflow: 'hidden', border: '1px solid var(--gray-200)',
                background: '#0f2416', boxShadow: '0 20px 48px rgba(10,34,16,0.1)'
              }}
            >
              <img 
                src="/assets/how_it_works_bg.jpg" 
                alt="Diagnostics mapping view" 
                style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.8 }}
              />
              {/* Hotspot node indicators */}
              <div className="animate-ping" style={{ position: 'absolute', top: '35%', left: '42%', width: '10px', height: '10px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 10px #fff' }} />
              <div className="animate-ping" style={{ position: 'absolute', top: '55%', left: '62%', width: '10px', height: '10px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 10px #fff' }} />
              <div className="animate-ping" style={{ position: 'absolute', top: '68%', left: '28%', width: '10px', height: '10px', borderRadius: '50%', background: '#fff', boxShadow: '0 0 10px #fff' }} />
              
              {/* Pill widget inside card */}
              <div style={{ position: 'absolute', bottom: '16px', left: '16px', background: 'rgba(255,255,255,0.92)', padding: '10px 14px', borderRadius: '12px', display: 'flex', gap: '8px', fontSize: '0.8rem', fontWeight: 800, color: 'var(--green-950)' }}>
                <span>🟢</span> Tomato Early Blight Active
              </div>
            </div>
          </div>

          {/* Right Column: Descriptions list */}
          <div>
            <div className="section-label" style={{ marginBottom: '12px' }}>AI Model Capabilities</div>
            <h2 style={{ color: 'var(--green-900)', fontSize: '2.4rem', fontWeight: 800, marginBottom: '20px', fontFamily: 'var(--font-serif)' }}>
              Deep Learning Diagnostic Suite
            </h2>
            <p style={{ color: 'var(--gray-600)', marginBottom: '32px', lineHeight: 1.6 }}>
              GreenScan processes leaf pixels to predict crop disease, calculates spatial contours, and provides agronomic remedies in natural language.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {technologies.map((t, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                  <div 
                    style={{ 
                      width: '42px', height: '42px', borderRadius: '50%', 
                      background: 'var(--green-100)', display: 'flex', alignItems: 'center', justifyContent: 'center', 
                      color: 'var(--green-800)', fontWeight: 800, fontSize: '0.9rem', flexShrink: 0
                    }}
                  >
                    0{idx + 1}
                  </div>
                  <div>
                    <h4 style={{ color: 'var(--gray-900)', margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 700, fontFamily: 'var(--font-serif)' }}>{t.name}</h4>
                    <p style={{ color: 'var(--gray-600)', fontSize: '0.88rem', margin: 0, lineHeight: 1.5 }}>{t.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  )
}

function FarmerExperienceSection() {
  const feedbacks = [
    {
      name: "Rajesh Patel",
      role: "Commercial Tomato Grower",
      location: "Gujarat, India",
      comment: "Early Blight was threatening my tomato crops this season. GreenScan diagnosed it from a simple leaf photo in 5 seconds. The organic treatment advice saved my harvest!",
      rating: 5,
      avatarColor: "#2e7d32"
    },
    {
      name: "Sophia Martinez",
      role: "AgriTech Field Researcher",
      location: "California, USA",
      comment: "The Grad‑CAM visual activation tab is stellar. It doesn't just output a prediction; it shows exactly where the neural network is looking. That transparency builds deep trust.",
      rating: 5,
      avatarColor: "#1b5e20"
    },
    {
      name: "John Mwangi",
      role: "Greenhouse Cooperative Lead",
      location: "Nakuru, Kenya",
      comment: "Perfect for field diagnostics. The simple plant health score (PHS) helped me quickly identify which greenhouse zones needed chemical control.",
      rating: 5,
      avatarColor: "#388e3c"
    },
    {
      name: "Clara Lindqvist",
      role: "Organic Greenhouse Operator",
      location: "Aland, Finland",
      comment: "I use the chatbot to ask follow-up questions about preventative spacing. It gives clear, chemical-free advice that aligns with my organic certification.",
      rating: 5,
      avatarColor: "#4caf50"
    }
  ]

  return (
    <div style={{ padding: '90px 20px', background: 'var(--green-50)', borderBottom: '1px solid var(--gray-200)' }}>
      <div className="container">
        
        <div style={{ textAlign: 'center', marginBottom: '60px' }}>
          <div className="section-label">Grower Stories</div>
          <h2 style={{ color: 'var(--green-900)', fontSize: '2.2rem', fontWeight: 800, fontFamily: 'var(--font-serif)' }}>Farmer Feedback & Comments</h2>
          <p style={{ color: 'var(--gray-600)', marginTop: '8px', maxWidth: '560px', margin: '8px auto 0' }}>
            Read real reviews from agriculturalists, growers, and researchers using GreenScan to monitor plant health.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
          {feedbacks.map((f, idx) => (
            <motion.div 
              key={idx}
              whileHover={{ y: -6 }}
              transition={{ duration: 0.2 }}
              className="card"
              style={{ 
                padding: '30px', 
                background: '#fff', 
                border: '1px solid var(--gray-200)', 
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: '0 10px 30px rgba(10, 34, 16, 0.03)'
              }}
            >
              <div>
                {/* Quotes & Stars */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <span style={{ fontSize: '2.5rem', color: 'var(--green-100)', fontFamily: 'serif', lineHeight: 0.1, marginTop: '20px' }}>“</span>
                  <div style={{ color: '#ffb300', fontSize: '0.85rem' }}>
                    {"★".repeat(f.rating)}
                  </div>
                </div>
                
                <p style={{ color: 'var(--gray-700)', fontSize: '0.92rem', lineHeight: '1.6', margin: '0 0 24px 0', fontStyle: 'italic' }}>
                  "{f.comment}"
                </p>
              </div>

              {/* User Bio */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', borderTop: '1px solid var(--gray-100)', paddingTop: '16px' }}>
                <div 
                  style={{ 
                    width: '42px', height: '42px', borderRadius: '50%', 
                    background: f.avatarColor, color: '#fff', 
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, fontSize: '0.95rem' 
                  }}
                >
                  {f.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--gray-900)', fontWeight: 800 }}>{f.name}</h4>
                  <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>{f.role}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--green-800)', fontWeight: 700, marginTop: '2px' }}>📍 {f.location}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

function FinalCTASection() {
  return (
    <section style={{ padding: '120px 20px', background: 'var(--green-100)', textAlign: 'center' }} aria-labelledby="final-cta-title">
      <div className="container">
        <h2 id="final-cta-title" style={{ fontSize: '2.4rem', fontWeight: 800, marginBottom: '24px', fontFamily: 'var(--font-serif)', color: 'var(--green-900)' }}>
          Ready to Check Your Plant?
        </h2>
        <p style={{ fontSize: '1.1rem', color: 'var(--gray-700)', maxWidth: '560px', margin: '0 auto 36px' }}>
          Upload a tomato leaf and explore GreenScan's AI‑powered health analysis.
        </p>
        <Link to="/scan" className="btn btn-primary btn-lg" style={{ textDecoration: 'none', padding: '14px 30px' }} aria-label="Start a Scan">
          Start a Scan
        </Link>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer style={{ background: '#0e1811', color: 'rgba(255,255,255,0.6)', padding: '70px 20px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '40px', marginBottom: '40px' }}>
          
          <div style={{ flex: '1 1 250px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Leaf size={24} color="var(--green-400)" />
              <span style={{ fontWeight: 800, fontSize: '1.3rem', color: '#fff', letterSpacing: '-0.02em' }}>GreenScan</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.6, maxWidth: '280px' }}>
              AI-powered plant health analysis. Diagnose leaf condition, visualize activations, and review farmer treatments.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '50px', flexWrap: 'wrap' }}>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>Navigation</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
                <li><Link to="/" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>Home</Link></li>
                <li><Link to="/scan" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>Scan</Link></li>
                <li><Link to="/history" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>History</Link></li>
              </ul>
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>Technology</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
                <li><a href="/#plant-health" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>Backbone CNN</a></li>
                <li><a href="/#plant-health" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>Grad-CAM Maps</a></li>
                <li><a href="/#plant-health" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>GSA Metrics</a></li>
              </ul>
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>Research</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
                <li><Link to="/about" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>About Page</Link></li>
                <li><Link to="/about" style={{ color: 'rgba(255,255,255,0.6)', textDecoration: 'none' }}>Validation</Link></li>
              </ul>
            </div>
          </div>

        </div>

        <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '20px', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: '10px', fontSize: '0.78rem', color: 'rgba(255,255,255,0.4)' }}>
          <span>© 2026 GreenScan Project. Research-grade AgriTech platform.</span>
          <span style={{ maxWidth: '420px', textAlign: 'right' }}>
            Disclaimer: GreenScan provides AI-assisted analysis and should not replace professional agricultural diagnosis.
          </span>
        </div>
      </div>
    </footer>
  )
}

export default function HomePage() {
  return (
    <motion.div 
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
      style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}
    >
      <HeroSection />
      <TrustSection />
      <HowItWorksSection />
      <TechnologyPipeline />
      <FarmerExperienceSection />
      <FeaturesSection />
      <FinalCTASection />
      <Footer />
    </motion.div>
  )
}
