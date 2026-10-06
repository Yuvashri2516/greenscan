import { useState, useRef, useEffect } from 'react'
import { sendChatMessage, getScanHistory, getFarmerProfile } from '../api/index.js'
import { MessageSquare, Send, Trash2, X, RefreshCw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import '../index.css'

const LANGUAGES = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'hi', label: 'हि', name: 'Hindi' },
  { code: 'ta', label: 'த',  name: 'Tamil' },
]

// Dynamic suggestion sets based on active scan state
const SUGGESTIONS_NO_SCAN_EN = [
  'How do I scan a leaf?',
  'What diseases can GreenScan detect?',
  'How can I prevent tomato diseases?',
  'What weather increases disease risk?',
]

const SUGGESTIONS_NO_SCAN_HI = [
  'मैं पत्ती स्कैन कैसे करूँ?',
  'ग्रीनस्कैन किन बीमारियों की पहचान कर सकता है?',
  'मैं टमाटर की बीमारियों से बचाव कैसे करूँ?',
  'किस मौसम में बीमारी का खतरा बढ़ता है?',
]

const SUGGESTIONS_NO_SCAN_TA = [
  'இலையை எவ்வாறு ஸ்கேன் செய்வது?',
  'கிரீன்ஸ்கேன் என்ன நோய்களைக் கண்டறியும்?',
  'தக்காளி நோய்களை எவ்வாறு தடுப்பது?',
  'எந்த வானிலை நோய் அபாயத்தை அதிகரிக்கும்?',
]

const SUGGESTIONS_SCAN_EN = [
  'What does my result mean?',
  'How serious is it?',
  'What should I do now?',
  'How can I prevent it?',
  'Will the weather affect it?',
]

const SUGGESTIONS_SCAN_HI = [
  'मेरे परिणाम का क्या मतलब है?',
  'यह कितना गंभीर है?',
  'मुझे अब क्या करना चाहिए?',
  'मैं इससे बचाव कैसे करूँ?',
  'क्या मौसम इसे प्रभावित करेगा?',
]

const SUGGESTIONS_SCAN_TA = [
  'என் முடிவின் அர்த்தம் என்ன?',
  'இது எவ்வளவு தீவிரமானது?',
  'இப்போது நான் என்ன செய்ய வேண்டும்?',
  'இதை எவ்வாறு தடுப்பது?',
  'வானிலை இதை பாதிக்குமா?',
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
        maxWidth: '85%',
        padding: '12px 16px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser ? 'var(--green-700)' : 'var(--white)',
        color: isUser ? '#fff' : 'var(--gray-900)',
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
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState('en')
  
  // Active context states
  const [activeScan, setActiveScan] = useState(result)
  const [farmerContext, setFarmerContext] = useState(null)
  const [weatherContext, setWeatherContext] = useState(null)

  const [messages, setMessages] = useState([])
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // 1. Sync scan result prop or retrieve from localStorage / backend history
  useEffect(() => {
    if (result) {
      setActiveScan(result)
      try { localStorage.setItem('greenscan_latest_scan', JSON.stringify(result)) } catch (e) {}
    } else {
      // Check localStorage cached scan
      try {
        const stored = localStorage.getItem('greenscan_latest_scan')
        if (stored) {
          setActiveScan(JSON.parse(stored))
        } else {
          // Fetch latest scan from history
          getScanHistory(1)
            .then(res => {
              if (res?.history && res.history.length > 0) {
                const item = res.history[0]
                const mappedScan = {
                  disease_name: item.disease_name,
                  display_name: item.display_name || item.disease_name,
                  confidence: item.confidence,
                  severity_level: item.severity_level,
                  plant_health_score: item.plant_health_score,
                  affected_area_pct: item.affected_area_pct,
                  treatment_priority: item.treatment_priority,
                  recommendations: item.recommendations,
                  disease_info: { display_name: item.display_name || item.disease_name }
                }
                setActiveScan(mappedScan)
              }
            })
            .catch(() => {})
        }
      } catch (e) {}
    }
  }, [result])

  // 2. Load farmer profile & weather context
  useEffect(() => {
    try {
      const storedProf = localStorage.getItem('greenscan_farmer_profile')
      if (storedProf) {
        setFarmerContext(JSON.parse(storedProf))
      } else {
        const storedId = localStorage.getItem('greenscan_farmer_id')
        if (storedId) {
          getFarmerProfile(storedId)
            .then(data => {
              if (data?.farmer) setFarmerContext(data.farmer)
            })
            .catch(() => {})
        }
      }

      const storedWeather = localStorage.getItem('greenscan_weather_data')
      if (storedWeather) {
        setWeatherContext(JSON.parse(storedWeather))
      }
    } catch (e) {}
  }, [open])

  // 3. Initialize greeting message when scan or language updates
  useEffect(() => {
    const farmerName = farmerContext?.name || ''
    const greetingName = farmerName ? `, ${farmerName}` : ''
    
    if (activeScan) {
      const name = activeScan.display_name || activeScan.disease_info?.display_name || 'Tomato Plant'
      const phs = activeScan.plant_health_score || activeScan.gsa_metrics?.plant_health_score || 100
      const sev = activeScan.severity_level || activeScan.gsa_metrics?.severity_level || 'Moderate'
      
      let initMsg = ''
      if (language === 'hi') {
        initMsg = `नमस्ते${greetingName}! मैंने आपके हालिया **${name}** स्कैन (स्वास्थ्य स्कोर: ${phs}/100, ${sev}) के परिणाम लोड कर लिए हैं। मैं आपकी फसल के लिए क्या सहायता कर सकता हूँ?`
      } else if (language === 'ta') {
        initMsg = `வணக்கம்${greetingName}! உங்கள் சமீபத்திய **${name}** ஸ்கேன் (ஆரோக்கிய மதிப்பெண்: ${phs}/100, ${sev}) முடிவுகள் ஏற்றப்பட்டுள்ளன. இன்று உங்கள் பயிர் பராமரிப்பில் எவ்வாறு உதவட்டும்?`
      } else {
        initMsg = `Hello${greetingName}! I've loaded your recent **${name}** scan (Health Score: ${phs}/100, Severity: ${sev}). How can I help you manage your crop today?`
      }

      setMessages([{ role: 'assistant', content: initMsg }])
    } else {
      let initMsg = ''
      if (language === 'hi') {
        initMsg = `नमस्ते${greetingName}! मैं ग्रीनस्कैन एआई हूँ। अभी तक कोई पत्ती स्कैन नहीं मिली है। एआई निदान और सलाह के लिए **Scan** टैब में जाकर फोटो अपलोड करें!`
      } else if (language === 'ta') {
        initMsg = `வணக்கம்${greetingName}! நான் கிரீன்ஸ்கேன் ஏஐ உதவியாளராவேன். சமீபத்திய இலை ஸ்கேன் எதுவுமில்லை. ஏஐ நோய் கண்டறிதலுக்கு **Scan** தாவலில் இலையை ஸ்கேன் செய்யவும்!`
      } else {
        initMsg = `Hello${greetingName}! I am GreenScan Assistant. I don't have a recent leaf scan yet. Please scan a tomato leaf in the **Scan** tab to get an AI diagnosis and personalized recommendations!`
      }

      setMessages([{ role: 'assistant', content: initMsg }])
    }
  }, [activeScan, language, farmerContext])

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      inputRef.current?.focus()
    }
  }, [open, messages])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return

    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    // Construct scan context payload
    let chatContext = null
    if (activeScan) {
      chatContext = {
        disease_name: activeScan.disease_name,
        display_name: activeScan.display_name || activeScan.disease_info?.display_name,
        confidence: activeScan.confidence,
        severity_level: activeScan.severity_level || activeScan.gsa_metrics?.severity_level,
        plant_health_score: activeScan.plant_health_score || activeScan.gsa_metrics?.plant_health_score,
        affected_area_pct: activeScan.affected_area_pct || activeScan.gsa_metrics?.affected_area_pct,
        recommendations: activeScan.recommendations,
        treatment_priority: activeScan.treatment_priority || activeScan.gsa_metrics?.treatment_priority,
        is_healthy: activeScan.disease_info?.is_healthy || activeScan.disease_name === 'tomato_healthy'
      }
    }

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
      const res = await sendChatMessage(
        msg, 
        language, 
        history, 
        chatContext,
        farmerContext,
        weatherContext
      )
      const replyContent = res.reply || res.response || 'I am unable to process that request right now.'
      setMessages(prev => [...prev, { role: 'assistant', content: replyContent }])
    } catch (e) {
      console.error(e)
      const errText = language === 'hi'
        ? 'संपर्क में समस्या आई। कृपया थोड़ी देर बाद पुनः प्रयास करें।'
        : language === 'ta'
        ? 'தொடர்பு கொள்வதில் சிக்கல் உள்ளது. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.'
        : 'I\'m having trouble connecting to the assistant right now. Your scan result is still safe. Please try again in a moment.'
      setMessages(prev => [...prev, { role: 'assistant', content: errText }])
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
    const farmerName = farmerContext?.name || ''
    const greetingName = farmerName ? `, ${farmerName}` : ''
    
    if (activeScan) {
      const name = activeScan.display_name || activeScan.disease_info?.display_name || 'Tomato Plant'
      const initMsg = language === 'hi'
        ? `चैट साफ़ हो गई! अपने **${name}** निदान के बारे में कुछ भी पूछें। 🍅`
        : language === 'ta'
        ? `அரட்டை அழிக்கப்பட்டது! உங்கள் **${name}** பற்றிய கேள்விகளைக் கேட்கலாம். 🍅`
        : `Chat cleared! Ask me anything about your **${name}** diagnosis. 🍅`
      setMessages([{ role: 'assistant', content: initMsg }])
    } else {
      const initMsg = language === 'hi'
        ? `चैट साफ़ हो गई! मैं आपकी क्या सहायता कर सकता हूँ? 🌿`
        : language === 'ta'
        ? `அரட்டை அழிக்கப்பட்டது! நான் உங்களுக்கு எவ்வாறு உதவட்டும்? 🌿`
        : `Chat cleared! How can I help you today? 🌿`
      setMessages([{ role: 'assistant', content: initMsg }])
    }
  }

  const suggestions = activeScan
    ? (language === 'hi' ? SUGGESTIONS_SCAN_HI : (language === 'ta' ? SUGGESTIONS_SCAN_TA : SUGGESTIONS_SCAN_EN))
    : (language === 'hi' ? SUGGESTIONS_NO_SCAN_HI : (language === 'ta' ? SUGGESTIONS_NO_SCAN_TA : SUGGESTIONS_NO_SCAN_EN))

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
              flex: 1, overflowY: 'auto', padding: '16px 20px',
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
                {suggestions.map(s => (
                  <button key={s} onClick={() => sendMessage(s)} style={{
                    padding: '5px 10px', borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--green-200)', background: 'var(--green-50)',
                    color: 'var(--green-800)', fontSize: '.75rem', fontWeight: 600, cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}>{s}</button>
                ))}
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
