// src/api/index.js – GreenScan API Client

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

async function handleResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

/** POST /predict – upload leaf image for disease detection */
export async function predictDisease(imageFile) {
  const form = new FormData()
  form.append('file', imageFile)
  const res = await fetch(`${BASE_URL}/predict`, { method: 'POST', body: form })
  return handleResponse(res)
}

/** GET /stores – nearby agricultural stores */
export async function getStores(lat, lon, radiusM = 25000) {
  const url = `${BASE_URL}/stores?lat=${lat}&lon=${lon}&radius=${radiusM}`
  const res = await fetch(url)
  return handleResponse(res)
}

/** POST /chat – multilingual chatbot */
export async function sendChatMessage(message, language = 'en', history = [], context = null) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, history, context }),
  })
  return handleResponse(res)
}

/** GET /history – retrieve scan history */
export async function getScanHistory(limit = 20) {
  const res = await fetch(`${BASE_URL}/history?limit=${limit}`)
  return handleResponse(res)
}

/** GET /disease – retrieve disease catalog information */
export async function getDiseaseCatalog(name = '') {
  const url = name ? `${BASE_URL}/disease?name=${encodeURIComponent(name)}` : `${BASE_URL}/disease`
  const res = await fetch(url)
  return handleResponse(res)
}


/** GET /tips – daily farming tips */
export async function getFarmingTips(count = 3) {
  const res = await fetch(`${BASE_URL}/tips?count=${count}`)
  return handleResponse(res)
}

/** GET /analytics – AI platform analytics */
export async function getAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics`)
  return handleResponse(res)
}

/** GET /research – AI research data */
export async function getResearch() {
  const res = await fetch(`${BASE_URL}/research`)
  return handleResponse(res)
}

/** GET /health – backend health check */
export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`)
  return handleResponse(res)
}

/** GET /weather – Real-time weather and fungal disease risk */
export async function getWeatherRisk(lat, lon) {
  const res = await fetch(`${BASE_URL}/weather?lat=${lat}&lon=${lon}`)
  return handleResponse(res)
}

/** POST /dosage – Calculate chemical/organic pesticide dosage */
export async function calculateDosage(payload) {
  const res = await fetch(`${BASE_URL}/dosage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return handleResponse(res)
}

/** POST /soil-health – Soil NPK & pH diagnostics */
export async function analyzeSoilHealth(payload) {
  const res = await fetch(`${BASE_URL}/soil-health`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return handleResponse(res)
}

