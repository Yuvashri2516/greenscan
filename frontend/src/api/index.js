// src/api/index.js – GreenScan API Client

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? 'https://greenscan-api-4rhz.onrender.com' : 'http://127.0.0.1:8001')
const BASE_URL = rawBaseUrl.replace(/\/+$/, '')

function formatErrorDetail(detail) {
  if (!detail) return 'Request failed'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(d => (typeof d === 'string' ? d : d.msg || d.message || JSON.stringify(d))).join(', ')
  }
  if (typeof detail === 'object') {
    return detail.msg || detail.message || detail.error || JSON.stringify(detail)
  }
  return String(detail)
}

async function fetchWithRetry(url, options = {}, retries = 3, backoff = 3000) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url, options)
      return res
    } catch (err) {
      if (i === retries - 1) throw err
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        await new Promise(resolve => setTimeout(resolve, backoff))
        continue
      }
      throw err
    }
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new Error(formatErrorDetail(err.detail || err.message || err.error))
  }
  return res.json()
}

/** POST /predict – upload leaf image for disease detection */
export async function predictDisease(imageFile, onStatusUpdate = null) {
  return predictDiseaseWithFarmer(imageFile, null, onStatusUpdate)
}

/** GET /stores – nearby agricultural stores */
export async function getStores(lat, lon, radiusM = 25000) {
  const url = `${BASE_URL}/stores?lat=${lat}&lon=${lon}&radius=${radiusM}`
  const res = await fetch(url)
  return handleResponse(res)
}

/** POST /chat – multilingual chatbot */
export async function sendChatMessage(message, language = 'en', history = [], context = null, farmerContext = null, weatherContext = null, historyTrend = null) {
  const res = await fetchWithRetry(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      message, 
      language, 
      history, 
      context,
      farmer_context: farmerContext,
      weather_context: weatherContext,
      history_trend: historyTrend
    }),
  })
  return handleResponse(res)
}

/** GET /history – retrieve scan history */
export async function getScanHistory(limit = 20) {
  const res = await fetchWithRetry(`${BASE_URL}/history?limit=${limit}`)
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
  const res = await fetchWithRetry(`${BASE_URL}/soil-health`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return handleResponse(res)
}


// ─── GreenScan 2.0: Farmer Profile API ───────────────────────────────────────

/** POST /farmers – Create a new farmer profile */
export async function createFarmerProfile(profile) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile)
  })
  return handleResponse(res)
}

/** GET /farmers/{id} – Get farmer profile (PIN excluded) */
export async function getFarmerProfile(farmerId) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers/${encodeURIComponent(farmerId)}`)
  return handleResponse(res)
}

/** PUT /farmers/{id} – Update farmer profile fields */
export async function updateFarmerProfile(farmerId, updates) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers/${encodeURIComponent(farmerId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  })
  return handleResponse(res)
}

/** POST /farmers/{id}/verify – Verify farmer PIN */
export async function verifyFarmerPin(farmerId, pin) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers/${encodeURIComponent(farmerId)}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pin })
  })
  return handleResponse(res)
}

/** GET /farmers/{id}/history – Farmer-specific scan history */
export async function getFarmerHistory(farmerId, limit = 20) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers/${encodeURIComponent(farmerId)}/history?limit=${limit}`)
  return handleResponse(res)
}

/** GET /farmers/{id}/trends – Health score and severity trend analysis */
export async function getFarmerTrends(farmerId, limit = 20) {
  const res = await fetchWithRetry(`${BASE_URL}/farmers/${encodeURIComponent(farmerId)}/trends?limit=${limit}`)
  return handleResponse(res)
}

/** POST /feedback – Submit user feedback */
export async function submitFeedback(rating, comment, category = null, farmerId = null) {
  const res = await fetch(`${BASE_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      rating,
      comment,
      category,
      farmer_id: farmerId
    })
  })
  return handleResponse(res)
}

// ─── GreenScan 2.0: Knowledge Base API ───────────────────────────────────────

/** GET /knowledge – List all disease keys in knowledge base */
export async function getKnowledgeIndex() {
  const res = await fetch(`${BASE_URL}/knowledge`)
  return handleResponse(res)
}

/** GET /knowledge/{diseaseKey} – Full knowledge base entry for a disease */
export async function getDiseaseKnowledge(diseaseKey) {
  const res = await fetch(`${BASE_URL}/knowledge/${encodeURIComponent(diseaseKey)}`)
  return handleResponse(res)
}

/**
 * Polls GET {BASE_URL}/health until it returns 200 with model_ready === true,
 * for up to maxWaitMs (150 seconds).
 */
export async function waitForModelReady(onStatusUpdate = null, maxWaitMs = 180000) {
  const startTime = Date.now()
  const intervalMs = 3000
  let hasNotifiedWakeup = false

  if (onStatusUpdate) {
    onStatusUpdate('Checking service status...')
  }

  while (Date.now() - startTime < maxWaitMs) {
    let isReady = false
    let isFetching = true

    // Show waking message if health check takes > 3s
    const uiTimeoutId = setTimeout(() => {
      if (isFetching && !hasNotifiedWakeup && onStatusUpdate) {
        hasNotifiedWakeup = true
        onStatusUpdate('Waking up the server, this can take up to 2 minutes...')
      }
    }, 3000)

    try {
      const controller = new AbortController()
      const fetchTimeout = setTimeout(() => controller.abort(), 90000) // 90s timeout for health check
      
      const res = await fetchWithRetry(`${BASE_URL}/health`, { signal: controller.signal }, 3, 5000)
      isFetching = false
      clearTimeout(uiTimeoutId)
      clearTimeout(fetchTimeout)
      
      if (res.ok) {
        const data = await res.json().catch(() => null)
        if (data && data.model_ready === true) {
          isReady = true
        } else if (!hasNotifiedWakeup && onStatusUpdate) {
          hasNotifiedWakeup = true
          onStatusUpdate('Warming up AI model...')
        }
      } else if (res.status !== 502 && res.status !== 503 && res.status !== 504) {
        // If it's a 500 or 404, it's not a cold start, it's a crash.
        throw new Error(`Server returned ${res.status}. Please check backend logs.`)
      } else if (!hasNotifiedWakeup && onStatusUpdate) {
        // 502/503 usually means Render is booting
        hasNotifiedWakeup = true
        onStatusUpdate('Waking up the server, this can take up to 2 minutes...')
      }
    } catch (err) {
      isFetching = false
      clearTimeout(uiTimeoutId)
      if (err.name !== 'AbortError' && !err.message.includes('fetch')) {
        throw err // Throw non-network/abort errors immediately
      }
      // Network errors or timeouts count as "not ready yet" - keep polling
    }

    if (isReady) {
      return true
    }

    if (Date.now() - startTime + intervalMs >= maxWaitMs) {
      break
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs))
  }

  throw new Error('The server is taking longer than usual to start. Please try again in a minute.')
}

/** POST /predict with optional farmer_id – extended version */
export async function predictDiseaseWithFarmer(imageFile, farmerId = null, onStatusUpdate = null) {
  const form = new FormData()
  form.append('file', imageFile)
  const url = farmerId
    ? `${BASE_URL}/predict?farmer_id=${encodeURIComponent(farmerId)}`
    : `${BASE_URL}/predict`

  // 1. Poll /health until server is ready before sending predict
  await waitForModelReady(onStatusUpdate)

  if (onStatusUpdate) {
    onStatusUpdate('Analyzing leaf image...')
  }

  const sendPredict = async () => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      controller.abort()
    }, 180000)

    try {
      const res = await fetchWithRetry(url, {
        method: 'POST',
        body: form,
        signal: controller.signal
      })
      clearTimeout(timeoutId)

      if (res.status === 502 || res.status === 503) {
        throw new Error('The server is temporarily unavailable. Please try again in a minute.')
      }

      return await handleResponse(res)
    } catch (err) {
      clearTimeout(timeoutId)
      if (err.name === 'AbortError') {
        throw new Error('Request timed out after 90 seconds. The server might still be waking up. Please try again.')
      }
      throw err
    }
  }

  return sendPredict()
}
