import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Leaf, ScanLine, History, BookOpen, Menu, X, Cpu, Activity, MessageSquare } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import '../index.css'

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  const navLinks = [
    { path: '/', label: 'Home', icon: <Leaf size={16} /> },
    { path: '/scan?tab=scan', label: 'Scan', icon: <ScanLine size={16} /> },
    { path: '/history', label: 'History', icon: <History size={16} /> },
    { path: '/disease-guide', label: 'Disease Information', icon: <BookOpen size={16} /> },
    { path: '/scan?tab=soil', label: 'Soil Advisor', icon: <Activity size={16} /> },
    { path: '/scan?tab=dosage', label: 'Dosage Calculator', icon: <Cpu size={16} /> },
    { path: '#', label: 'AI Assistant', icon: <MessageSquare size={16} />, isChat: true },
  ]

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true)
      } else {
        setScrolled(false)
      }
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const isActive = (path) => {
    if (path.includes('?')) {
      const [basePath, query] = path.split('?')
      return location.pathname === basePath && location.search.includes(query)
    }
    return location.pathname === path
  }

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  const closeMobileMenu = () => setMobileMenuOpen(false)

  const handleLinkClick = (link, e) => {
    closeMobileMenu()
    if (link.isChat) {
      e.preventDefault()
      const toggleBtn = document.getElementById('chatbot-toggle')
      if (toggleBtn) {
        toggleBtn.click()
      } else {
        navigate('/scan?chat=true')
      }
      return
    }
    if (link.isAnchor) {
      e.preventDefault()
      if (location.pathname !== '/') {
        navigate('/' + link.path)
        setTimeout(() => {
          const el = document.getElementById(link.path.replace('#', ''))
          if (el) el.scrollIntoView({ behavior: 'smooth' })
        }, 150)
      } else {
        const el = document.getElementById(link.path.replace('#', ''))
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  return (
    <motion.header 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'sticky', top: 0, zIndex: 1000,
        background: scrolled ? 'rgba(255, 255, 255, 0.95)' : 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: scrolled ? '1px solid rgba(10, 34, 16, 0.08)' : '1px solid var(--gray-200)',
        boxShadow: scrolled ? 'var(--shadow-md)' : 'none',
        transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
      }}
    >
      <div className="container" style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: '76px', padding: '0 24px'
      }}>
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={closeMobileMenu}>
          <motion.div 
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
            style={{
              background: 'linear-gradient(135deg, var(--green-600) 0%, var(--green-800) 100%)', 
              width: 38, height: 38,
              borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(38, 107, 55, 0.15)'
            }}
          >
            <Leaf size={18} color="#fff" />
          </motion.div>
          <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gray-900)', letterSpacing: '-0.02em' }}>
            Green<span style={{ color: 'var(--green-700)' }}>Scan</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hide-mobile" style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          {navLinks.map((link) => (
            <motion.div 
              key={link.label} 
              whileHover={{ scale: 1.02 }} 
              whileTap={{ scale: 0.98 }}
              style={{ position: 'relative' }}
            >
              <Link 
                to={link.path} 
                onClick={(e) => handleLinkClick(link, e)}
                className={`tab-btn ${isActive(link.path) ? 'active' : ''}`}
                style={{ 
                  textDecoration: 'none', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '6px',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-md)',
                  color: isActive(link.path) ? 'var(--green-800)' : 'var(--gray-700)',
                  background: isActive(link.path) ? 'var(--green-50)' : 'transparent',
                  fontWeight: 600,
                  fontSize: '0.85rem'
                }}
              >
                {link.icon} {link.label}
              </Link>
            </motion.div>
          ))}
          
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ marginLeft: '12px' }}>
            <Link 
              to="/scan?tab=scan" 
              className="btn btn-primary" 
              style={{ 
                textDecoration: 'none', 
                borderRadius: 'var(--radius-md)', 
                padding: '9px 18px', 
                fontSize: '0.85rem',
                fontWeight: 700
              }}
            >
              Start Scanning
            </Link>
          </motion.div>
        </nav>

        {/* Hamburger Menu Toggle (Mobile) */}
        <button 
          className="hide-desktop btn" 
          onClick={toggleMobileMenu}
          aria-label="Toggle Navigation Menu"
          style={{ background: 'transparent', padding: '8px', color: 'var(--green-900)' }}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            style={{
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              borderBottom: '1px solid var(--gray-200)',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              padding: '12px 24px 20px',
              gap: '8px',
              position: 'absolute',
              top: '76px', left: 0, right: 0,
              boxShadow: 'var(--shadow-md)',
              zIndex: 1000
            }}
          >
            {navLinks.map((link) => (
              <Link 
                key={link.label}
                to={link.path}
                onClick={(e) => handleLinkClick(link, e)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '12px',
                  padding: '12px 14px', borderRadius: '8px',
                  textDecoration: 'none', fontWeight: 600,
                  background: isActive(link.path) ? 'var(--green-100)' : 'transparent',
                  color: isActive(link.path) ? 'var(--green-800)' : 'var(--gray-700)',
                  fontSize: '0.95rem'
                }}
              >
                {link.icon} {link.label}
              </Link>
            ))}

            <Link 
              to="/scan?tab=scan" 
              className="btn btn-primary" 
              onClick={closeMobileMenu}
              style={{ textDecoration: 'none', textAlign: 'center', padding: '12px', borderRadius: '8px', display: 'block', width: '100%', fontSize: '0.95rem', fontWeight: 700, marginTop: '8px' }}
            >
              Start Scanning
            </Link>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @media (max-width: 1024px) {
          .hide-mobile { display: none !important; }
        }
        @media (min-width: 1025px) {
          .hide-desktop { display: none !important; }
        }
      `}</style>
    </motion.header>
  )
}
