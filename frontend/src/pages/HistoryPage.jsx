import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getScanHistory } from '../api/index.js'
import { motion, AnimatePresence } from 'framer-motion'
import { Calendar, Activity, ShieldAlert, Award, FileText, ArrowRight, RefreshCw, X, AlertTriangle, Search, Filter } from 'lucide-react'
import '../index.css'

export default function HistoryPage() {
  const [historyList, setHistoryList] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedScan, setSelectedScan] = useState(null)

  // Filters & Sorting state
  const [searchTerm, setSearchTerm] = useState('')
  const [diseaseFilter, setDiseaseFilter] = useState('all')
  const [severityFilter, setSeverityFilter] = useState('all')
  const [sortBy, setSortBy] = useState('newest')

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const data = await getScanHistory(50)
      setHistoryList(data.history || [])
      setError(null)
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoString) => {
    try {
      const d = new Date(isoString + 'Z') // SQLite dates are stored in UTC
      return d.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (e) {
      return isoString
    }
  }

  const getSeverityBadgeClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'healthy': return 'badge-green'
      case 'mild': return 'badge-yellow'
      case 'moderate': return 'badge-yellow'
      case 'severe': return 'badge-red'
      default: return 'badge-gray'
    }
  }

  const getSeverityTraffic = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'healthy': return '🟢'
      case 'mild': return '🟡'
      case 'moderate': return '🟠'
      case 'severe': return '🔴'
      default: return '⚪'
    }
  }

  const resetFilters = () => {
    setSearchTerm('')
    setDiseaseFilter('all')
    setSeverityFilter('all')
    setSortBy('newest')
  }

  // Extract unique disease names for filter dropdown
  const uniqueDiseases = Array.from(new Set(historyList.map(item => item.display_name).filter(Boolean)))

  // Apply filters and sorting logic
  const filteredList = historyList
    .filter(item => {
      const term = searchTerm.toLowerCase().trim()
      if (!term) return true
      return (
        item.display_name?.toLowerCase().includes(term) ||
        item.disease_name?.toLowerCase().includes(term) ||
        item.severity_level?.toLowerCase().includes(term)
      )
    })
    .filter(item => {
      if (diseaseFilter === 'all') return true
      return item.display_name === diseaseFilter
    })
    .filter(item => {
      if (severityFilter === 'all') return true
      return item.severity_level?.toLowerCase() === severityFilter.toLowerCase()
    })
    .sort((a, b) => {
      if (sortBy === 'newest') return new Date(b.timestamp) - new Date(a.timestamp)
      if (sortBy === 'oldest') return new Date(a.timestamp) - new Date(b.timestamp)
      if (sortBy === 'confidence') return b.confidence - a.confidence
      if (sortBy === 'health_score') return b.plant_health_score - a.plant_health_score
      return 0
    })

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0 }} 
      transition={{ duration: 0.5 }}
      style={{ minHeight: '100vh', background: 'var(--green-50)', padding: 'var(--sp-8) 0' }}
    >
      <div className="container">
        
        {/* Title Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px', marginBottom: 'var(--sp-8)' }}>
          <div>
            <h1 style={{ color: 'var(--green-900)', margin: 0, fontWeight: 800 }}>Scan History Logs</h1>
            <p style={{ color: 'var(--gray-600)', marginTop: '6px' }}>Review past tomato leaf diagnoses and agronomic treatment recommendations.</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              className="btn btn-secondary" 
              onClick={fetchHistory} 
              disabled={loading}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <RefreshCw size={16} className={loading ? 'animate-pulse' : ''} /> Refresh
            </button>
            <Link to="/scan" className="btn btn-primary" style={{ textDecoration: 'none' }}>
              Scan New Leaf
            </Link>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
            {[1, 2, 3].map(i => (
              <div key={i} className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div className="skeleton skeleton-title" style={{ width: '50%', margin: 0 }} />
                  <div className="skeleton" style={{ width: '80px', height: '22px', borderRadius: 'var(--radius-full)' }} />
                </div>
                <div className="skeleton skeleton-text" style={{ width: '40%' }} />
                <div className="skeleton skeleton-text" style={{ width: '90%', height: '10px' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                  <div className="skeleton skeleton-circle" style={{ width: '32px', height: '32px' }} />
                  <div className="skeleton skeleton-text" style={{ width: '25%', height: '10px', margin: 0 }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="alert alert-danger" style={{ maxWidth: '600px', margin: '0 auto var(--sp-6)', textAlign: 'center' }}>
            <AlertTriangle size={24} style={{ margin: '0 auto 10px', display: 'block' }} />
            <p style={{ margin: 0, fontWeight: 600 }}>{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && historyList.length === 0 && (
          <div className="card" style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center', padding: '60px 40px' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--green-100)', display: 'flex', alignItems: 'center', justifyContents: 'center', margin: '0 auto 24px', justifyContent: 'center' }}>
              <FileText size={40} color="var(--green-800)" />
            </div>
            <h3 style={{ color: 'var(--gray-900)', fontSize: '1.4rem', marginBottom: '12px' }}>No scans yet</h3>
            <p style={{ color: 'var(--gray-600)', maxWidth: '400px', margin: '0 auto 24px', lineHeight: 1.6 }}>
              Your analyzed plants will appear here.
            </p>
            <Link to="/scan" className="btn btn-primary" style={{ textDecoration: 'none' }}>
              Start Scanning
            </Link>
          </div>
        )}

        {/* Filters Controls (Visible only if there are scans loaded) */}
        {!loading && !error && historyList.length > 0 && (
          <div 
            className="card" 
            style={{ 
              padding: '20px', 
              background: '#fff', 
              border: '1px solid var(--gray-200)', 
              borderRadius: 'var(--radius-md)',
              marginBottom: '24px',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '16px',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            {/* Search Input */}
            <div style={{ position: 'relative', flex: '1 1 240px' }}>
              <Search size={16} color="var(--gray-400)" style={{ position: 'absolute', left: '14px', top: '15px' }} />
              <input 
                type="text" 
                className="input" 
                style={{ paddingLeft: '38px', borderRadius: 'var(--radius-md)' }} 
                placeholder="Search scans by disease or severity..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Select Dropdowns Row */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', flex: '2 1 400px', justifyContent: 'flex-end' }}>
              
              {/* Disease Dropdown */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--gray-500)', fontWeight: 700 }}>Condition:</span>
                <select 
                  className="input" 
                  style={{ width: '150px', padding: '8px 12px', fontSize: '0.85rem', borderRadius: 'var(--radius-md)' }}
                  value={diseaseFilter}
                  onChange={(e) => setDiseaseFilter(e.target.value)}
                >
                  <option value="all">All Conditions</option>
                  {uniqueDiseases.map(name => <option key={name} value={name}>{name}</option>)}
                </select>
              </div>

              {/* Severity Dropdown */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--gray-500)', fontWeight: 700 }}>Severity:</span>
                <select 
                  className="input" 
                  style={{ width: '130px', padding: '8px 12px', fontSize: '0.85rem', borderRadius: 'var(--radius-md)' }}
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                >
                  <option value="all">All Severities</option>
                  <option value="healthy">Healthy</option>
                  <option value="mild">Mild</option>
                  <option value="moderate">Moderate</option>
                  <option value="severe">Severe</option>
                </select>
              </div>

              {/* Sorting Dropdown */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--gray-500)', fontWeight: 700 }}>Sort By:</span>
                <select 
                  className="input" 
                  style={{ width: '140px', padding: '8px 12px', fontSize: '0.85rem', borderRadius: 'var(--radius-md)' }}
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="newest">Newest Scans</option>
                  <option value="oldest">Oldest Scans</option>
                  <option value="confidence">AI Confidence</option>
                  <option value="health_score">Health Score</option>
                </select>
              </div>

              {/* Reset button */}
              {(searchTerm || diseaseFilter !== 'all' || severityFilter !== 'all' || sortBy !== 'newest') && (
                <button 
                  className="btn btn-ghost btn-sm" 
                  onClick={resetFilters}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', borderRadius: '6px' }}
                >
                  Clear Filters
                </button>
              )}

            </div>
          </div>
        )}

        {/* Filtered empty state */}
        {!loading && !error && historyList.length > 0 && filteredList.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '40px', background: '#fff' }}>
            <AlertTriangle size={32} color="var(--accent-orange)" style={{ margin: '0 auto 12px' }} />
            <h3 style={{ color: 'var(--gray-900)', fontSize: '1.2rem', marginBottom: '8px' }}>No Matching Records</h3>
            <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', marginBottom: '20px' }}>
              We couldn't find any scan logs matching your current search parameters.
            </p>
            <button className="btn btn-primary" onClick={resetFilters}>Reset Search Filters</button>
          </div>
        )}

        {/* Logs Table / Cards Grid */}
        {!loading && !error && filteredList.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Desktop View Table */}
            <div className="card hide-mobile" style={{ padding: 0, overflow: 'hidden', background: '#fff', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-md)' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'var(--gray-50)', borderBottom: '1px solid var(--gray-200)' }}>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>Diagnosis Result</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>Date & Time</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>AI Confidence</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>Health Score</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>Severity Level</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700 }}>Affected Area</th>
                    <th style={{ padding: '16px 24px', color: 'var(--gray-900)', fontWeight: 700, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredList.map((scan) => (
                    <tr 
                      key={scan.id} 
                      style={{ borderBottom: '1px solid var(--gray-100)', transition: 'background 0.2s' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'var(--green-50)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ padding: '18px 24px', fontWeight: 700, color: 'var(--gray-900)' }}>
                        {getSeverityTraffic(scan.severity_level)} {scan.display_name}
                      </td>
                      <td style={{ padding: '18px 24px', color: 'var(--gray-600)', fontSize: '0.88rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <Calendar size={14} /> {formatDate(scan.timestamp)}
                        </div>
                      </td>
                      <td style={{ padding: '18px 24px', fontWeight: 700, color: 'var(--gray-700)' }}>
                        {scan.confidence.toFixed(1)}%
                      </td>
                      <td style={{ padding: '18px 24px' }}>
                        <span style={{ fontWeight: 800, color: 'var(--green-800)' }}>{scan.plant_health_score}</span>
                        <span style={{ color: 'var(--gray-400)', fontSize: '0.8rem' }}>/100</span>
                      </td>
                      <td style={{ padding: '18px 24px' }}>
                        <span className={`badge ${getSeverityBadgeClass(scan.severity_level)}`}>
                          {scan.severity_level}
                        </span>
                      </td>
                      <td style={{ padding: '18px 24px', fontWeight: 700, color: 'var(--gray-700)', fontSize: '0.88rem' }}>
                        {scan.affected_area_pct !== undefined && scan.affected_area_pct !== null ? `${scan.affected_area_pct.toFixed(1)}%` : 'Information unavailable'}
                      </td>
                      <td style={{ padding: '18px 24px', textAlign: 'right' }}>
                        <button 
                          className="btn btn-ghost btn-sm"
                          onClick={() => setSelectedScan(scan)}
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', borderRadius: '6px' }}
                        >
                          Details <ArrowRight size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile View Grid */}
            <div className="hide-desktop" style={{ display: 'none', flexDirection: 'column', gap: '16px' }}>
              {filteredList.map((scan) => (
                <div key={scan.id} className="card" style={{ padding: '20px', background: '#fff', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
                      <span className={`badge ${getSeverityBadgeClass(scan.severity_level)}`} style={{ marginBottom: '6px' }}>
                        {getSeverityTraffic(scan.severity_level)} {scan.severity_level}
                      </span>
                      <h4 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--gray-900)', fontWeight: 700 }}>{scan.display_name}</h4>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--green-800)' }}>{scan.plant_health_score}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--gray-400)', display: 'block' }}>PHS</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--gray-500)', borderTop: '1px solid var(--gray-100)', paddingTop: '10px' }}>
                    <span>Conf: <strong>{scan.confidence.toFixed(1)}%</strong></span>
                    <span>Area: <strong>{scan.affected_area_pct !== undefined && scan.affected_area_pct !== null ? `${scan.affected_area_pct.toFixed(1)}%` : 'Information unavailable'}</strong></span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={12} /> {formatDate(scan.timestamp).split(',')[0]}</span>
                  </div>
                  <button 
                    className="btn btn-secondary btn-sm btn-full"
                    onClick={() => setSelectedScan(scan)}
                    style={{ marginTop: '12px', borderRadius: '6px' }}
                  >
                    View Details
                  </button>
                </div>
              ))}
            </div>

            {/* CSS helper to toggle table/cards on mobile */}
            <style>{`
              @media (max-width: 768px) {
                .hide-mobile { display: none !important; }
                .hide-desktop { display: flex !important; }
              }
            `}</style>
          </div>
        )}
      </div>

      {/* Details Dialog Modal */}
      <AnimatePresence>
        {selectedScan && (
          <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
            backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', padding: '20px', zIndex: 'var(--z-modal)'
          }}>
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card"
              style={{
                width: '100%', maxWidth: '650px', maxHeight: '90vh',
                overflowY: 'auto', padding: '32px', position: 'relative',
                boxShadow: 'var(--shadow-lg)', background: '#fff', border: '1px solid var(--gray-200)',
                borderRadius: 'var(--radius-md)'
              }}
            >
              <button 
                onClick={() => setSelectedScan(null)}
                style={{
                  position: 'absolute', top: '20px', right: '20px',
                  background: 'var(--gray-100)', border: 'none', borderRadius: '50%',
                  width: '36px', height: '36px', display: 'flex',
                  alignItems: 'center', justifyContents: 'center', cursor: 'pointer',
                  justifyContent: 'center', color: 'var(--gray-600)'
                }}
              >
                <X size={20} />
              </button>

              <div style={{ borderBottom: '1px solid var(--gray-200)', pb: '16px', marginBottom: '24px', paddingBottom: '16px' }}>
                <span className={`badge ${getSeverityBadgeClass(selectedScan.severity_level)}`} style={{ marginBottom: '8px' }}>
                  {getSeverityTraffic(selectedScan.severity_level)} {selectedScan.severity_level} Severity
                </span>
                <h2 style={{ color: 'var(--gray-900)', margin: 0, fontWeight: 800 }}>{selectedScan.display_name}</h2>
                <p style={{ color: 'var(--gray-500)', margin: '4px 0 0', fontSize: '0.85rem' }}>
                  Logged on {formatDate(selectedScan.timestamp)}
                </p>
              </div>

              {/* Core Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                <div style={{ background: 'var(--gray-50)', padding: '16px', borderRadius: '8px', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
                  <Award size={20} color="var(--green-700)" style={{ margin: '0 auto 6px' }} />
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--gray-500)' }}>Health Score</p>
                  <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--green-800)' }}>{selectedScan.plant_health_score}/100</p>
                </div>
                <div style={{ background: 'var(--gray-50)', padding: '16px', borderRadius: '8px', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
                  <Activity size={20} color="var(--green-700)" style={{ margin: '0 auto 6px' }} />
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--gray-500)' }}>Confidence</p>
                  <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--gray-800)' }}>{selectedScan.confidence.toFixed(1)}%</p>
                </div>
                <div style={{ background: 'var(--gray-50)', padding: '16px', borderRadius: '8px', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
                  <ShieldAlert size={20} color="var(--green-700)" style={{ margin: '0 auto 6px' }} />
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--gray-500)' }}>Affected Region</p>
                  <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--gray-800)' }}>{selectedScan.affected_area_pct.toFixed(1)}%</p>
                </div>
              </div>

              {/* Treatment Protocols */}
              {selectedScan.recommendations && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {selectedScan.recommendations.organic_plan?.length > 0 && (
                    <div>
                      <h4 style={{ margin: '0 0 8px', color: 'var(--green-800)', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 800 }}>🌱 Organic Remedies</h4>
                      <ul style={{ paddingLeft: '20px', margin: 0, color: 'var(--gray-700)', fontSize: '0.88rem', lineHeight: '1.5' }}>
                        {selectedScan.recommendations.organic_plan.map((item, idx) => <li key={idx}>{item}</li>)}
                      </ul>
                    </div>
                  )}

                  {selectedScan.recommendations.chemical_plan?.length > 0 && (
                    <div>
                      <h4 style={{ margin: '0 0 8px', color: 'var(--accent-orange)', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 800 }}>🧪 Chemical Treatment</h4>
                      <ul style={{ paddingLeft: '20px', margin: 0, color: 'var(--gray-700)', fontSize: '0.88rem', lineHeight: '1.5' }}>
                        {selectedScan.recommendations.chemical_plan.map((item, idx) => <li key={idx}>{item}</li>)}
                      </ul>
                    </div>
                  )}

                  {selectedScan.recommendations.prevention_plan?.length > 0 && (
                    <div>
                      <h4 style={{ margin: '0 0 8px', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 800 }}>🛡️ Preventative Action Stems</h4>
                      <ul style={{ paddingLeft: '20px', margin: 0, color: 'var(--gray-700)', fontSize: '0.88rem', lineHeight: '1.5' }}>
                        {selectedScan.recommendations.prevention_plan.map((item, idx) => <li key={idx}>{item}</li>)}
                      </ul>
                    </div>
                  )}

                  {selectedScan.treatment_priority && (
                    <div style={{ background: '#F1F8E9', padding: '16px', borderRadius: '8px', borderLeft: '4px solid var(--green-700)', marginTop: '8px' }}>
                      <p style={{ margin: '0 0 4px', fontSize: '0.78rem', fontWeight: 800, color: 'var(--green-900)' }}>⚠️ PRIORITY INSTRUCTIONS:</p>
                      <p style={{ margin: 0, color: 'var(--gray-800)', fontSize: '0.88rem', lineHeight: 1.4 }}>{selectedScan.treatment_priority}</p>
                    </div>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', gap: '12px', marginTop: '32px', borderTop: '1px solid var(--gray-200)', paddingTop: '20px' }}>
                <Link to="/scan" className="btn btn-primary" style={{ textDecoration: 'none', flex: 1, borderRadius: '6px' }} onClick={() => setSelectedScan(null)}>
                  Scan Again
                </Link>
                <button className="btn btn-secondary" style={{ flex: 1, borderRadius: '6px' }} onClick={() => setSelectedScan(null)}>
                  Close Logs
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
