import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../api/index.js'
import { MessageSquare, Send, Trash2, X, RefreshCw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import '../index.css'

const LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'hi', label: 'हि', name: 'Hindi' },
  { code: 'ta', label: 'த',  name: 'Tamil' },
]

const SUGGESTIONS = [
  'What does my disease result mean?',
  'How serious is this?',
  'What should I do next?',
  'How can I prevent it?',
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '16px',
    }}>
      {!isUser && (
        <div style={{
          width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
          background: 'linear-gradient(135deg, var(--green-600), var(--green-800))', display: 'flex',
          alignItems: 'center', justifyContent: 'center', fontSize: '13px',
          marginRight: 8, marginTop: 2, boxShadow: 'var(--shadow-sm)', color: '#fff',
          fontWeight: 'bold'
        }}>🌿</div>
      )}
      <div style={{
        maxWidth: '80%',
        padding: '12px 16px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser ? 'var(--green-700)' : 'var(--white)',
        color: isUser ? '#fff' : 'var(--gray-800)',
        fontSize: '0.88rem',
        lineHeight: 1.5,
        boxShadow: 'var(--shadow-sm)',
        border: isUser ? 'none' : '1px solid var(--gray-200)',
        whiteSpace: 'pre-wrap',
      }}>
        {msg.content}
      </div>
    </div>
  )
}

export default function Chatbot({ result = null }) {
  const [open, setOpen]       = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "No active plant scan. Start a scan to discuss your plant analysis." }
  ])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState('en')
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      inputRef.current?.focus()
    }
  }, [open, messages])

  // Update initial message based on context if context becomes available
  useEffect(() => {
    if (result && result.disease_info) {
      setMessages([
        { 
          role: 'assistant', 
          content: `Hello! I've loaded the diagnostic context for your **${result.display_name || result.disease_info.display_name}** scan. I can help you understand this diagnosis and provide simple treatment guidance.` 
        }
      ])
    }
  }, [result])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return

    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    // Build context object matching backend expected keys
    let chatContext = null
    if (result && result.disease_info) {
      chatContext = {
        disease_name: result.disease_name,
        display_name: result.display_name || result.disease_info.display_name,
        confidence: result.confidence,
        severity_level: result.gsa_metrics?.severity_level,
        plant_health_score: result.gsa_metrics?.plant_health_score,
        recommendations: result.recommendations,
        treatment_priority: result.gsa_metrics?.treatment_priority
      }
    }

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
      const res = await sendChatMessage(msg, language, history, chatContext)
      const replyContent = res.reply || res.response || 'Sorry, I couldn\'t process that question.'
      setMessages(prev => [...prev, { role: 'assistant', content: replyContent }])
    } catch (e) {
      console.error(e)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    if (result && result.disease_info) {
      setMessages([
        { 
          role: 'assistant', 
          content: `Chat cleared! Ask me anything about your **${result.display_name || result.disease_info.display_name}** diagnosis. 🍅` 
        }
      ])
    } else {
      setMessages([{ role: 'assistant', content: "Chat cleared! How can I help you? 🌿" }])
    }
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        id="chatbot-toggle"
        onClick={() => setOpen(v => !v)}
        style={{
          position: 'fixed', bottom: 24, right: 24,
          width: 60, height: 60,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #166534, #16a34a)',
          color: '#fff', border: 'none', cursor: 'pointer',
          boxShadow: '0 6px 24px rgba(22,101,52,.45), 0 2px 8px rgba(0,0,0,.2)',
          zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          transform: open ? 'scale(1.08)' : 'scale(1)',
          outline: 'none',
        }}
        onMouseEnter={e => { e.currentTarget.style.transform = 'scale(1.12)'; e.currentTarget.style.boxShadow = '0 8px 28px rgba(22,101,52,.5), 0 2px 8px rgba(0,0,0,.25)' }}
        onMouseLeave={e => { e.currentTarget.style.transform = open ? 'scale(1.08)' : 'scale(1)'; e.currentTarget.style.boxShadow = '0 6px 24px rgba(22,101,52,.45), 0 2px 8px rgba(0,0,0,.2)' }}
        title="Open farming assistant"
        aria-label="Toggle chatbot"
      >
        {open ? <X size={26} /> : <MessageSquare size={26} />}
      </button>

      {/* Chat panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            style={{
              position: 'fixed', bottom: 92, right: 24,
              width: 380, maxWidth: 'calc(100vw - 32px)',
              height: 540, maxHeight: 'calc(100vh - 120px)',
              background: 'var(--white)',
              borderRadius: 'var(--radius-xl)',
              boxShadow: 'var(--shadow-lg)',
              border: '1px solid var(--green-200)',
              display: 'flex', flexDirection: 'column',
              overflow: 'hidden',
              zIndex: 9999,
            }}
          >
            {/* Panel header */}
            <div style={{
              background: 'linear-gradient(135deg, var(--green-800), var(--green-600))',
              padding: '16px 20px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: 34, height: 34, borderRadius: '50%',
                  background: 'rgba(255,255,255,.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, color: '#fff'
                }}>🌿</div>
                <div>
                  <p style={{ color: '#fff', fontWeight: 800, fontSize: '.92rem', lineHeight: 1.1, margin: 0 }}>GreenScan Assistant</p>
                  <p style={{ color: 'rgba(255,255,255,.75)', fontSize: '.72rem', margin: '2px 0 0' }}>Context-Aware Support</p>
                </div>
              </div>
              
              {/* Language selector & trash */}
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                {LANGUAGES.map(l => (
                  <button key={l.code} onClick={() => setLanguage(l.code)} title={l.name} style={{
                    padding: '3px 8px', borderRadius: 'var(--radius-full)',
                    border: 'none', cursor: 'pointer', fontSize: '.72rem', fontWeight: 700,
                    background: language === l.code ? 'rgba(255,255,255,.95)' : 'rgba(255,255,255,.15)',
                    color: language === l.code ? 'var(--green-800)' : 'rgba(255,255,255,.9)',
                    transition: 'all 0.2s ease',
                  }}>{l.label}</button>
                ))}
                <button onClick={clearChat} title="Clear chat" style={{
                  marginLeft: 4, background: 'rgba(255,255,255,.15)', border: 'none',
                  color: '#fff', cursor: 'pointer',
                  borderRadius: '50%', width: 26, height: 26, display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <Trash2 size={13} />
                </button>
              </div>
            </div>

            {/* Messages view */}
            <div style={{
              flex: 1, overflowY: 'auto', padding: '20px',
              background: 'var(--gray-50)',
            }}>
              {messages.map((msg, i) => <Message key={i} msg={msg} />)}
              {loading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '16px' }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: '50%',
                    background: 'var(--green-700)', display: 'flex',
                    alignItems: 'center', justifyContent: 'center', fontSize: 13, color: '#fff'
                  }}>🌿</div>
                  <div style={{
                    background: 'var(--white)', border: '1px solid var(--gray-200)',
                    borderRadius: '16px 16px 16px 4px', padding: '10px 14px',
                    display: 'flex', gap: 6, alignItems: 'center',
                  }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{
                        width: 6, height: 6, borderRadius: '50%', background: 'var(--green-600)',
                        animation: `pulse-green 1.2s ${i * 0.2}s infinite`,
                      }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Suggestions panel */}
            {messages.length <= 1 && (
              <div style={{ padding: '8px 12px', display: 'flex', gap: 6, flexWrap: 'wrap', borderTop: '1px solid var(--gray-100)', background: 'var(--gray-50)' }}>
                {SUGGESTIONS.map(s => {
                  if (result && result.disease_info?.is_healthy && (s.includes('disease') || s.includes('treat'))) return null;
                  return (
                    <button key={s} onClick={() => sendMessage(s)} style={{
                      padding: '5px 10px', borderRadius: 'var(--radius-full)',
                      border: '1px solid var(--green-200)', background: 'var(--green-50)',
                      color: 'var(--green-800)', fontSize: '.75rem', fontWeight: 600, cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}>{s}</button>
                  )
                })}
              </div>
            )}

            {/* Input field row */}
            <div style={{
              padding: '12px 16px',
              borderTop: '1px solid var(--gray-200)',
              display: 'flex', gap: '8px',
              background: 'var(--white)',
              alignItems: 'center'
            }}>
              <input
                ref={inputRef}
                className="input"
                style={{ flex: 1, borderRadius: 'var(--radius-full)', padding: '10px 16px', fontSize: '.88rem' }}
                placeholder={language === 'hi' ? 'अपना सवाल लिखें…' : language === 'ta' ? 'கேள்வி கேளுங்கள்…' : 'Ask about plant diseases…'}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={loading}
                id="chat-input"
              />
              <button
                className="btn btn-primary"
                style={{ borderRadius: '50%', width: 40, height: 40, padding: 0, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                id="chat-send-btn"
              >
                {loading ? <RefreshCw size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={16} />}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
