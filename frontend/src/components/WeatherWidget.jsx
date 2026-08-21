import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CloudRain, Thermometer, Wind, Droplets, AlertTriangle, ShieldCheck, MapPin } from 'lucide-react'
import { getWeatherRisk } from '../api'

const PRESET_LOCATIONS = [
  { name: 'Chennai, Tamil Nadu', lat: 13.0827, lon: 80.2707 },
  { name: 'New Delhi, Delhi', lat: 28.6139, lon: 77.2090 },
  { name: 'Bengaluru, Karnataka', lat: 12.9716, lon: 77.5946 },
  { name: 'Nashik, Maharashtra', lat: 19.9975, lon: 73.7898 },
  { name: 'Guntur, Andhra Pradesh', lat: 16.3067, lon: 80.4365 },
  { name: 'Nagpur, Maharashtra', lat: 21.1458, lon: 79.0882 },
]

export default function WeatherWidget() {
  const [weatherData, setWeatherData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)
  const [errorType, setErrorType] = useState(null) // 'location-denied', 'api-failure', 'network-failure'
  const [selectedLocation, setSelectedLocation] = useState({
    name: 'Chennai, Tamil Nadu',
    lat: 13.0827,
    lon: 80.2707,
  })
  const [showLocationSelector, setShowLocationSelector] = useState(false)
  const [customLat, setCustomLat] = useState('13.0827')
  const [customLon, setCustomLon] = useState('80.2707')

  useEffect(() => {
    requestBrowserGeolocation()
  }, [])

  const requestBrowserGeolocation = () => {
    setLoading(true)
    setErrorMsg(null)
    setErrorType(null)

    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude
          const lon = pos.coords.longitude
          setSelectedLocation({
            name: `My Geolocation (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
            lat,
            lon,
          })
          fetchWeather(lat, lon)
        },
        (err) => {
          console.warn("Geolocation warning/error:", err)
          if (err.code === 1) {
            // Permission Denied
            setErrorType('location-denied')
            setErrorMsg('Location access is required to provide local weather risk analysis.')
            setLoading(false)
          } else {
            // Other geolocation errors (timeout, position unavailable)
            setErrorType('network-failure')
            setErrorMsg('Unable to detect geolocation. Reverting to default fallback location.')
            // Fallback to Chennai
            setSelectedLocation({
              name: 'Chennai, Tamil Nadu',
              lat: 13.0827,
              lon: 80.2707,
            })
            fetchWeather(13.0827, 80.2707)
          }
        },
        { timeout: 8000 }
      )
    } else {
      setErrorType('network-failure')
      setErrorMsg('Browser geolocation is not supported. Reverting to default fallback location.')
      fetchWeather(selectedLocation.lat, selectedLocation.lon)
    }
  }

  const fetchWeather = async (lat, lon) => {
    setLoading(true)
    setErrorMsg(null)
    setErrorType(null)
    try {
      const res = await getWeatherRisk(lat, lon)
      if (res && res.status === 'success') {
        setWeatherData(res)
      } else {
        setErrorType('api-failure')
        setErrorMsg('Weather data is temporarily unavailable.')
      }
    } catch (err) {
      console.error(err)
      if (!navigator.onLine) {
        setErrorType('network-failure')
        setErrorMsg('Unable to connect to the weather service.')
      } else {
        setErrorType('api-failure')
        setErrorMsg('Weather data is temporarily unavailable.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPreset = (e) => {
    const idx = parseInt(e.target.value)
    if (isNaN(idx)) return
    const loc = PRESET_LOCATIONS[idx]
    setSelectedLocation(loc)
    setCustomLat(loc.lat.toString())
    setCustomLon(loc.lon.toString())
    fetchWeather(loc.lat, loc.lon)
    setShowLocationSelector(false)
  }

  const handleCustomSubmit = (e) => {
    e.preventDefault()
    const lat = parseFloat(customLat)
    const lon = parseFloat(customLon)
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      alert("Please enter valid decimal coordinates (Lat: -90 to 90, Lon: -180 to 180)")
      return
    }
    const locName = `Custom Coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)})`
    setSelectedLocation({ name: locName, lat, lon })
    fetchWeather(lat, lon)
    setShowLocationSelector(false)
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="card" 
      style={{ padding: '32px', background: '#fff', border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', gap: '24px' }}
    >
      {/* Header Panel */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--gray-900)', fontWeight: 800 }}>🌤️ Weather & Risk Radar</h2>
          <p style={{ margin: '4px 0 0', color: 'var(--gray-500)', fontSize: '0.9rem' }}>Micro-climate monitoring & fungal pathogen risk prediction</p>
        </div>
        
        {/* Dynamic Location Banner */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--gray-100)', padding: '8px 16px', borderRadius: 'var(--radius-full)', border: '1px solid var(--gray-200)' }}>
          <MapPin size={16} color="var(--green-700)" />
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--gray-700)' }}>{selectedLocation.name}</span>
        </div>
      </div>

      {/* Geolocation Controls & Selector */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', borderBottom: '1px solid var(--gray-200)', paddingBottom: '16px' }}>
        <button 
          onClick={requestBrowserGeolocation} 
          className="btn btn-ghost" 
          style={{ fontSize: '0.82rem', padding: '8px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          📍 Use My Location
        </button>
        <button 
          onClick={() => setShowLocationSelector(!showLocationSelector)} 
          className="btn btn-ghost" 
          style={{ fontSize: '0.82rem', padding: '8px 16px', borderRadius: '8px' }}
        >
          {showLocationSelector ? '✕ Close Selector' : '🗺️ Change Location'}
        </button>
      </div>

      {/* Expandable Location Selector Pane */}
      {showLocationSelector && (
        <motion.div 
          initial={{ opacity: 0, height: 0 }} 
          animate={{ opacity: 1, height: 'auto' }}
          style={{ background: 'var(--gray-50)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--gray-200)', display: 'flex', flexDirection: 'column', gap: '16px' }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--gray-700)' }}>Select preset farming region:</label>
            <select onChange={handleSelectPreset} defaultValue="" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--gray-300)', background: '#fff', fontSize: '0.88rem' }}>
              <option value="" disabled>-- Choose a preset --</option>
              {PRESET_LOCATIONS.map((loc, idx) => (
                <option key={idx} value={idx}>{loc.name} ({loc.lat}, {loc.lon})</option>
              ))}
            </select>
          </div>

          <div style={{ borderTop: '1px solid var(--gray-200)', paddingTop: '16px' }}>
            <form onSubmit={handleCustomSubmit} style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: '120px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--gray-700)' }}>Latitude</label>
                <input type="text" value={customLat} onChange={(e) => setCustomLat(e.target.value)} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.88rem' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: '120px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--gray-700)' }}>Longitude</label>
                <input type="text" value={customLon} onChange={(e) => setCustomLon(e.target.value)} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.88rem' }} />
              </div>
              <button type="submit" className="btn btn-primary" style={{ padding: '10px 20px', borderRadius: '6px', fontSize: '0.88rem', fontWeight: 700 }}>
                Set Coordinates
              </button>
            </form>
          </div>
        </motion.div>
      )}

      {/* Main States (Loading, Errors, or Success Views) */}
      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--gray-500)' }}>
          <span className="spinner spinner-green" style={{ width: '28px', height: '28px', margin: '0 auto 12px', display: 'block' }} />
          <p style={{ margin: 0, fontWeight: 700 }}>Analyzing local weather conditions...</p>
        </div>
      ) : errorType === 'location-denied' ? (
        <div style={{ padding: '24px', background: '#ffebee', border: '1px solid var(--accent-red)20', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
          <AlertTriangle size={32} color="var(--accent-red)" style={{ margin: '0 auto 10px', display: 'block' }} />
          <p style={{ margin: '0 0 16px', color: 'var(--accent-red)', fontWeight: 800, fontSize: '0.95rem' }}>
            {errorMsg}
          </p>
          <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', border: '1px solid var(--gray-200)', maxWidth: '400px', margin: '0 auto', textAlign: 'left' }}>
            <h4 style={{ margin: '0 0 10px', color: 'var(--gray-800)', fontSize: '0.88rem', fontWeight: 800 }}>Please choose a location to load data:</h4>
            <select onChange={handleSelectPreset} defaultValue="" style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.85rem' }}>
              <option value="" disabled>-- Select preset region --</option>
              {PRESET_LOCATIONS.map((loc, idx) => (
                <option key={idx} value={idx}>{loc.name}</option>
              ))}
            </select>
          </div>
        </div>
      ) : errorType ? (
        <div style={{ padding: '32px', background: '#ffebee', border: '1px solid var(--accent-red)20', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
          <AlertTriangle size={32} color="var(--accent-red)" style={{ margin: '0 auto 10px', display: 'block' }} />
          <p style={{ margin: 0, color: 'var(--accent-red)', fontWeight: 800 }}>{errorMsg}</p>
        </div>
      ) : weatherData ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Fungal disease risk banner */}
          <div style={{ 
            background: weatherData.disease_risk.color + '15', 
            border: `1px solid ${weatherData.disease_risk.color}30`, 
            padding: '20px 24px', 
            borderRadius: 'var(--radius-md)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between', 
            flexWrap: 'wrap', 
            gap: '16px' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <AlertTriangle size={24} color={weatherData.disease_risk.color} />
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>FUNGAL PATHOGEN RISK INDEX</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--gray-900)' }}>
                  {weatherData.disease_risk.level} Disease Risk ({weatherData.disease_risk.score}%)
                </div>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'var(--gray-50)', padding: '20px 16px', borderRadius: 'var(--radius-md)', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
              <Thermometer size={24} style={{ color: 'var(--accent-orange)', marginBottom: '6px' }} />
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700 }}>Temperature</p>
              <p style={{ margin: '4px 0 0', fontSize: '1.3rem', fontWeight: 800, color: 'var(--gray-900)' }}>{weatherData.temperature_c}°C</p>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: '20px 16px', borderRadius: 'var(--radius-md)', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
              <Droplets size={24} style={{ color: 'var(--blue-500)', marginBottom: '6px' }} />
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700 }}>Humidity</p>
              <p style={{ margin: '4px 0 0', fontSize: '1.3rem', fontWeight: 800, color: 'var(--gray-900)' }}>{weatherData.humidity_pct}%</p>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: '20px 16px', borderRadius: 'var(--radius-md)', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
              <CloudRain size={24} style={{ color: 'var(--blue-600)', marginBottom: '6px' }} />
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700 }}>Rain Probability</p>
              <p style={{ margin: '4px 0 0', fontSize: '1.3rem', fontWeight: 800, color: 'var(--gray-900)' }}>{weatherData.rain_probability_pct}%</p>
            </div>
            <div style={{ background: 'var(--gray-50)', padding: '20px 16px', borderRadius: 'var(--radius-md)', textAlign: 'center', border: '1px solid var(--gray-200)' }}>
              <Wind size={24} style={{ color: 'var(--gray-600)', marginBottom: '6px' }} />
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--gray-500)', fontWeight: 700 }}>Wind Speed</p>
              <p style={{ margin: '4px 0 0', fontSize: '1.3rem', fontWeight: 800, color: 'var(--gray-900)' }}>{weatherData.windspeed_kmh} km/h</p>
            </div>
          </div>

          {/* Detailed Advisor Box */}
          <div style={{ background: '#fcfcfc', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
            <div style={{ borderLeft: `5px solid ${weatherData.disease_risk.color}`, padding: '20px 24px' }}>
              <h4 style={{ margin: '0 0 10px', color: 'var(--green-900)', fontSize: '0.95rem', fontWeight: 800 }}>💡 Disease Risk & Environmental Analysis</h4>
              <p style={{ margin: '0 0 16px', color: 'var(--gray-700)', fontSize: '0.9rem', lineHeight: '1.5' }}>
                {weatherData.disease_risk.recommendation}
              </p>
              
              {/* Factors list */}
              {weatherData.disease_risk.risk_factors && weatherData.disease_risk.risk_factors.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--gray-400)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Active Contributing Factors:</span>
                  <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--gray-600)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '6px', lineHeight: 1.4 }}>
                    {weatherData.disease_risk.risk_factors.map((factor, idx) => (
                      <li key={idx}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            {/* Warning Explanation Notice */}
            <div style={{ background: 'var(--gray-50)', padding: '12px 24px', borderTop: '1px solid var(--gray-200)', fontSize: '0.76rem', color: 'var(--gray-500)', lineHeight: 1.4 }}>
              * <strong>Note:</strong> Risk is estimated from environmental micro-climate conditions and does not confirm physical pathogen presence. Routine field scouting is recommended.
            </div>
          </div>
        </div>
      ) : (
        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--gray-500)' }}>
          <p>Choose a location to compute local fungal risk.</p>
        </div>
      )}
    </motion.div>
  )
}
