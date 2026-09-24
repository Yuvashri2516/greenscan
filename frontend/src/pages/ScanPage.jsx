import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import UploadSection from '../components/UploadSection.jsx'
import ResultPanel from '../components/ResultPanel.jsx'
import RecommendationPanel from '../components/RecommendationPanel.jsx'
import SeverityPanel from '../components/SeverityPanel.jsx'
import GradCAMPanel from '../components/GradCAMPanel.jsx'
import ProgressionPanel from '../components/ProgressionPanel.jsx'
import ReportDownload from '../components/ReportDownload.jsx'
import Chatbot from '../components/Chatbot.jsx'
import WeatherWidget from '../components/WeatherWidget.jsx'
import DosageCalculator from '../components/DosageCalculator.jsx'
import SoilAdvisor from '../components/SoilAdvisor.jsx'
import PlantHealthGuide from '../components/PlantHealthGuide.jsx'
import { motion } from 'framer-motion'
import { CloudSun, Calculator, Sprout, Activity, AlertTriangle, CheckCircle } from 'lucide-react'
import '../index.css';
import ScanHeader from '../components/ScanHeader.jsx';

export default function ScanPage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') || 'scan'

  const setActiveTab = (tab) => {
    setSearchParams({ tab })
  }

  // Trigger opening chatbot if requested via navigation
  useEffect(() => {
    if (searchParams.get('chat') === 'true') {
      const timer = setTimeout(() => {
        const btn = document.getElementById('chatbot-toggle')
        if (btn) btn.click()
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [searchParams])

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      exit={{ opacity: 0 }} 
      transition={{ duration: 0.5 }}
      style={{ display: 'flex', flexDirection: 'column', background: 'var(--gray-50)', paddingBottom: '60px' }}
    >
      <div className="container" style={{ padding: 'var(--sp-8) var(--sp-6)', flexGrow: 1 }}>
        <ScanHeader />

        {/* Tools Navigation Tabs */}
        <div style={{ display: 'inline-flex', gap: '8px', background: '#fff', padding: '6px', borderRadius: 'var(--radius-full)', boxShadow: 'var(--shadow-sm)', marginTop: '20px', border: '1px solid var(--gray-200)', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button 
            onClick={() => setActiveTab('scan')} 
            className="btn" 
            style={{ background: activeTab === 'scan' ? 'var(--green-700)' : 'transparent', color: activeTab === 'scan' ? '#fff' : 'var(--gray-700)', borderRadius: 'var(--radius-full)', padding: '8px 20px', fontSize: '0.9rem' }}
          >
            <Activity size={16} style={{ marginRight: '6px' }} /> AI Leaf Scan
          </button>
          <button 
            onClick={() => setActiveTab('weather')} 
            className="btn" 
            style={{ background: activeTab === 'weather' ? 'var(--green-700)' : 'transparent', color: activeTab === 'weather' ? '#fff' : 'var(--gray-700)', borderRadius: 'var(--radius-full)', padding: '8px 20px', fontSize: '0.9rem' }}
          >
            <CloudSun size={16} style={{ marginRight: '6px' }} /> Weather & Risk Radar
          </button>
          <button 
            onClick={() => setActiveTab('dosage')} 
            className="btn" 
            style={{ background: activeTab === 'dosage' ? 'var(--green-700)' : 'transparent', color: activeTab === 'dosage' ? '#fff' : 'var(--gray-700)', borderRadius: 'var(--radius-full)', padding: '8px 20px', fontSize: '0.9rem' }}
          >
            <Calculator size={16} style={{ marginRight: '6px' }} /> Dosage Calculator
          </button>
          <button 
            onClick={() => setActiveTab('soil')} 
            className="btn" 
            style={{ background: activeTab === 'soil' ? 'var(--green-700)' : 'transparent', color: activeTab === 'soil' ? '#fff' : 'var(--gray-700)', borderRadius: 'var(--radius-full)', padding: '8px 20px', fontSize: '0.9rem' }}
          >
            <Sprout size={16} style={{ marginRight: '6px' }} /> Soil Advisor
          </button>
        </div>
      </div>

      {/* Tab 1: AI Leaf Scan */}
      {activeTab === 'scan' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: (result || loading) ? 'minmax(340px, 420px) 1fr' : '1fr',
          gap: '28px',
          alignItems: 'start',
          maxWidth: (result || loading) ? 1240 : 680,
          margin: '0 auto',
          padding: '0 24px',
          width: '100%'
        }}>
          {/* Left column: Upload + Report */}
          <div style={{ position: 'sticky', top: '90px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <UploadSection onResult={setResult} onLoading={setLoading} />
            {result && <ReportDownload result={result} />}
          </div>

          {/* Right column: Diagnosis & Analytics Loading Skeleton */}
          {loading && !result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', minWidth: 0, width: '100%' }}>
              <div className="card" style={{ padding: '0', overflow: 'hidden', border: '1px solid var(--gray-200)' }}>
                <div style={{ background: 'var(--gray-50)', padding: '24px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <div className="skeleton skeleton-title" style={{ width: '50%', margin: 0 }} />
                    <div className="skeleton skeleton-text" style={{ width: '35%', height: '10px', marginTop: '8px' }} />
                  </div>
                  <div className="skeleton skeleton-circle" style={{ width: '56px', height: '56px' }} />
                </div>
              </div>
              
              <div className="card" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '20px', background: '#fff', border: '1px solid var(--gray-200)' }}>
                <div>
                  <div className="skeleton skeleton-title" style={{ width: '40%', height: '18px' }} />
                  <div className="skeleton skeleton-text" style={{ width: '60%', height: '10px' }} />
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', alignItems: 'center' }}>
                  <div className="skeleton" style={{ width: '100%', aspectRatio: '1.2/1', borderRadius: '12px' }} />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div className="skeleton skeleton-title" style={{ width: '50%', height: '14px' }} />
                    <div className="skeleton skeleton-text" />
                    <div className="skeleton skeleton-text" style={{ width: '80%' }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Right column: Diagnosis & Analytics Results */}
          {result && !loading && (() => {
            // GreenScan 2.0: Check if validation failed
            const valStatus = result.validation_status || result.validation?.status;
            const isRejected = valStatus === 'NOT_TOMATO_LEAF' || valStatus === 'LOW_QUALITY_IMAGE';

            if (isRejected) {
              const isNotLeaf = valStatus === 'NOT_TOMATO_LEAF';
              return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', minWidth: 0 }}>
                  {/* Validation Rejection Banner */}
                  <div style={{
                    background: isNotLeaf ? 'rgba(245,158,11,0.08)' : 'rgba(239,68,68,0.08)',
                    border: `1px solid ${isNotLeaf ? 'rgba(245,158,11,0.4)' : 'rgba(239,68,68,0.4)'}`,
                    borderRadius: 18, padding: '2rem', textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                      {isNotLeaf ? '🍃' : '📷'}
                    </div>
                    <div style={{ color: isNotLeaf ? '#f59e0b' : '#ef4444', fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.75rem' }}>
                      {isNotLeaf ? 'Not a Valid Tomato Leaf Image' : 'Image Quality Too Low'}
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem', lineHeight: 1.6 }}>
                      {result.message || result.validation?.message}
                    </div>
                    {(result.user_guidance || result.validation?.message) && (
                      <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 12, padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', textAlign: 'left', lineHeight: 1.7 }}>
                        💡 <strong>Tips:</strong> {result.user_guidance}
                      </div>
                    )}
                  </div>
                </div>
              );
            }

            // Valid scan — show full results
            return (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', minWidth: 0 }}>
                {/* Validation status badge (soft warning or valid) */}
                {result.validation && (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '0.6rem',
                    padding: '0.6rem 1rem', borderRadius: 10,
                    background: result.validation.confidence_warning
                      ? 'rgba(245,158,11,0.08)' : 'rgba(16,185,129,0.07)',
                    border: `1px solid ${
                      result.validation.confidence_warning
                        ? 'rgba(245,158,11,0.25)' : 'rgba(16,185,129,0.2)'
                    }`,
                    fontSize: '0.85rem'
                  }}>
                    {result.validation.confidence_warning
                      ? <AlertTriangle size={15} color="#f59e0b" />
                      : <CheckCircle size={15} color="var(--primary-green)" />}
                    <span style={{ color: result.validation.confidence_warning ? '#f59e0b' : 'var(--primary-green)' }}>
                      {result.validation.confidence_warning
                        ? `Low confidence (${result.confidence}%). Capture a clearer, closer image for more reliable results.`
                        : `Valid tomato leaf — leaf coverage: ${result.validation.leaf_coverage_pct?.toFixed(1)}%`}
                    </span>
                  </div>
                )}

                <ResultPanel result={result} />

                {/* GreenScan 2.0: Structured Plant Health Guide */}
                {result.structured_recommendation && (
                  <PlantHealthGuide
                    recommendation={result.structured_recommendation}
                    validationInfo={result.validation}
                  />
                )}

                {result.progression && <ProgressionPanel progression={result.progression} />}
              </div>
            );
          })()}
        </div>
      )}

      {/* Tab 2: Weather & Risk Radar */}
      {activeTab === 'weather' && (
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px', width: '100%' }}>
          <WeatherWidget />
        </div>
      )}

      {/* Tab 3: Dosage Calculator */}
      {activeTab === 'dosage' && (
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px', width: '100%' }}>
          <DosageCalculator 
            initialDisease={result?.prediction || 'tomato_Early blight'} 
            initialSeverity={result?.severity || 'Moderate'} 
          />
        </div>
      )}

      {/* Tab 4: Soil Health Advisor */}
      {activeTab === 'soil' && (
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px', width: '100%' }}>
          <SoilAdvisor />
        </div>
      )}

      <Chatbot result={result} />
    </motion.div>
  )
}
