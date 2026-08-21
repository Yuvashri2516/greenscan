import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UploadCloud, Camera, Image as ImageIcon, AlertCircle, FileText } from 'lucide-react'
import { predictDisease } from '../api/index.js'
import '../index.css'

export default function UploadSection({ onResult, onLoading = () => {} }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  
  // Loading cycling state
  const [loadingStep, setLoadingStep] = useState(0)

  useEffect(() => {
    onLoading(loading)
  }, [loading, onLoading])

  const fileInputRef = useRef(null)
  const cameraInputRef = useRef(null)

  const loadingMessages = [
    "Preparing image...",
    "Identifying disease...",
    "Analyzing visual patterns...",
    "Estimating plant health...",
    "Preparing recommendations..."
  ]

  // Cycle loading messages sequentially during model execution
  useEffect(() => {
    let interval = null
    if (loading) {
      setLoadingStep(0)
      interval = setInterval(() => {
        setLoadingStep((prev) => {
          if (prev < loadingMessages.length - 1) {
            return prev + 1
          }
          return prev
        })
      }, 1200)
    } else {
      setLoadingStep(0)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [loading])

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0])
    }
  }

  const processFile = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload a valid image file such as JPG or PNG.')
      return
    }
    setError(null)
    setFile(selectedFile)
    const reader = new FileReader()
    reader.onload = () => setPreview(reader.result)
    reader.readAsDataURL(selectedFile)
    onResult(null) // clear previous diagnosis
  }

  const handlePredict = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    try {
      const data = await predictDisease(file)
      onResult({ ...data, _preview: preview })
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleUseDemoImage = async () => {
    setLoading(true)
    setError(null)
    onResult(null)
    try {
      const { DEMO_IMAGE_BASE64 } = await import('../api/demoImage.js')
      setPreview(DEMO_IMAGE_BASE64)
      const resBlob = await fetch(DEMO_IMAGE_BASE64)
      const blob = await resBlob.blob()
      const demoFile = new File([blob], 'demo_tomato_leaf.jpg', { type: 'image/jpeg' })
      setFile(demoFile)
      
      const data = await predictDisease(demoFile)
      onResult({ ...data, _preview: DEMO_IMAGE_BASE64 })
    } catch (err) {
      console.error(err)
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const clearSelection = () => {
    setFile(null)
    setPreview(null)
    setError(null)
    onResult(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    if (cameraInputRef.current) cameraInputRef.current.value = ''
  }

  const formatSize = (bytes) => {
    if (!bytes) return ''
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    return `${(kb / 1024).toFixed(1)} MB`
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.5 }}
      className="card" 
      style={{ padding: '36px', border: '1px solid var(--gray-200)', background: '#fff', borderRadius: 'var(--radius-md)' }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h2 style={{ color: 'var(--green-900)', marginBottom: '6px', fontSize: '1.4rem', fontWeight: 800 }}>
        🌿 Scan Tomato Leaf
      </h2>
      <p style={{ color: 'var(--gray-600)', marginBottom: '24px', fontSize: '0.9rem' }}>
        Select a file from your device gallery or snap a photo using your camera to verify crop condition.
      </p>

      {isDragging && (
        <div style={{ padding: '40px 0', border: '2px dashed var(--green-600)', background: 'var(--green-100)', borderRadius: 'var(--radius-md)', textAlign: 'center', color: 'var(--green-800)', fontWeight: 700, marginBottom: '20px' }}>
          Drop leaf image here...
        </div>
      )}

      {!preview && !isDragging && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Touch-Friendly Action Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
            <div 
              onClick={() => cameraInputRef.current?.click()}
              className="glow-hover"
              style={{ 
                padding: '30px 20px', cursor: 'pointer', textAlign: 'center', 
                background: 'var(--gray-50)', border: '1px solid var(--gray-200)', 
                borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', gap: '12px', transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--green-400)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--gray-200)'}
            >
              <Camera size={36} color="var(--green-700)" />
              <div style={{ fontWeight: 800, color: 'var(--gray-900)', fontSize: '0.95rem' }}>📷 Capture Leaf</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Use camera directly</div>
            </div>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="glow-hover"
              style={{ 
                padding: '30px 20px', cursor: 'pointer', textAlign: 'center', 
                background: 'var(--gray-50)', border: '1px solid var(--gray-200)', 
                borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', gap: '12px', transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--green-400)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--gray-200)'}
            >
              <ImageIcon size={36} color="var(--green-700)" />
              <div style={{ fontWeight: 800, color: 'var(--gray-900)', fontSize: '0.95rem' }}>🖼 Upload From Gallery</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Select leaf files</div>
            </div>

            <div 
              onClick={handleUseDemoImage}
              className="glow-hover"
              id="demo-scan-btn"
              style={{ 
                padding: '30px 20px', cursor: 'pointer', textAlign: 'center', 
                background: 'var(--gray-50)', border: '1px solid var(--gray-200)', 
                borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', gap: '12px', transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--green-400)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--gray-200)'}
            >
              <UploadCloud size={36} color="var(--green-700)" />
              <div style={{ fontWeight: 800, color: 'var(--gray-900)', fontSize: '0.95rem' }}>🧪 Scan Demo Leaf</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--gray-500)' }}>Test backend flow</div>
            </div>
          </div>

          {/* Desktop drag-and-drop prompt */}
          <div style={{ textAlign: 'center', border: '1px dashed var(--gray-200)', padding: '20px', borderRadius: 'var(--radius-md)', color: 'var(--gray-500)', fontSize: '0.82rem' }}>
            <UploadCloud size={20} style={{ margin: '0 auto 6px', display: 'block', opacity: 0.6 }} />
            Drag and drop files directly into this panel to begin scanning.
          </div>

          {/* Hidden HTML input triggers */}
          <input
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            ref={fileInputRef}
            onChange={handleFileChange}
            id="gallery-input"
          />
          <input
            type="file"
            accept="image/*"
            capture="environment"
            style={{ display: 'none' }}
            ref={cameraInputRef}
            onChange={handleFileChange}
            id="camera-input"
          />
        </div>
      )}

      {preview && !isDragging && (
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Selected Preview Area */}
          <div style={{ position: 'relative', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--gray-200)', background: 'var(--gray-50)', padding: '8px' }}>
            <img src={preview} alt="Selected Leaf Mockup" style={{ width: '100%', maxHeight: '300px', objectFit: 'contain', borderRadius: '8px', display: 'block', margin: '0 auto' }} />
          </div>

          {/* Metadata */}
          {file && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'var(--gray-100)', padding: '10px 16px', borderRadius: '8px', fontSize: '0.82rem', color: 'var(--gray-600)' }}>
              <FileText size={14} />
              <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
                {file.name}
              </div>
              <div style={{ flexShrink: 0 }}>
                {formatSize(file.size)}
              </div>
            </div>
          )}

          {/* Loading Animation States */}
          {loading && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', padding: '18px 0', background: 'var(--green-100)', borderRadius: 'var(--radius-md)', border: '1px solid var(--green-200)' }}>
              <span className="spinner spinner-green" style={{ width: '24px', height: '24px' }} />
              <p style={{ margin: 0, fontWeight: 700, color: 'var(--green-800)', fontSize: '0.9rem' }} className="animate-pulse">
                {loadingMessages[loadingStep]}
              </p>
            </div>
          )}

          {/* Decision Buttons */}
          {!loading && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              <button
                onClick={handlePredict}
                className="btn btn-primary"
                id="analyze-leaf-btn"
                style={{ padding: '14px', borderRadius: 'var(--radius-md)', fontSize: '0.95rem', fontWeight: 700 }}
              >
                Analyze Leaf
              </button>
              <button 
                onClick={clearSelection}
                className="btn btn-ghost"
                id="retake-btn"
                style={{ padding: '14px', borderRadius: 'var(--radius-md)', fontSize: '0.95rem' }}
              >
                Choose Another / Retake
              </button>
            </div>
          )}
        </motion.div>
      )}

      {/* Error Alert Panel */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0 }}
            className="alert alert-danger" 
            style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px', borderRadius: 'var(--radius-md)', padding: '14px' }}
          >
            <AlertCircle size={16} /> {error}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
