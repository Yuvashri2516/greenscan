// src/components/StoreLocator.jsx
import { useState, useEffect, useRef } from 'react'
import { getStores } from '../api/index.js'
import { useLocation } from '../hooks/useLocation.js'

export default function StoreLocator() {
  const { location, loading: locLoading, error: locError, getLocation, searchByCity } = useLocation()
  const [stores, setStores]     = useState([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [isDemo, setIsDemo]     = useState(false)
  const [cityInput, setCityInput] = useState('')
  const mapRef      = useRef(null)
  const mapInstance = useRef(null)
  const markersRef  = useRef([])

  // Fetch stores when location changes
  useEffect(() => {
    if (!location) return
    setLoading(true)
    setError(null)
    getStores(location.lat, location.lon, 25000)
      .then(data => {
        setStores(data.stores || [])
        setIsDemo(data.is_demo || false)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [location])

  // Initialize / update Leaflet map
  useEffect(() => {
    if (!location || !stores.length || !mapRef.current) return

    const L = window.L
    if (!L) return

    // Init map once
    if (!mapInstance.current) {
      mapInstance.current = L.map(mapRef.current).setView([location.lat, location.lon], 13)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(mapInstance.current)
    } else {
      mapInstance.current.setView([location.lat, location.lon], 13)
    }

    // Clear old markers
    markersRef.current.forEach(m => m.remove())
    markersRef.current = []

    // User marker
    const userIcon = L.divIcon({
      html: `<div style="background:var(--green-700);width:14px;height:14px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.4)"></div>`,
      className: '', iconSize: [14, 14], iconAnchor: [7, 7],
    })
    markersRef.current.push(
      L.marker([location.lat, location.lon], { icon: userIcon })
        .addTo(mapInstance.current)
        .bindPopup('<b>📍 Your Location</b>')
    )

    // Store markers
    stores.forEach(s => {
      if (!s.lat || !s.lon) return
      const icon = L.divIcon({
        html: `<div style="background:#e74c3c;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>`,
        className: '', iconSize: [12, 12], iconAnchor: [6, 6],
      })
      markersRef.current.push(
        L.marker([s.lat, s.lon], { icon })
          .addTo(mapInstance.current)
          .bindPopup(`<b>🏪 ${s.name}</b><br><small>${s.address}</small><br><small>${s.distance_km} km away</small>`)
      )
    })

    // Fit bounds to all markers
    if (markersRef.current.length > 1) {
      const group = L.featureGroup(markersRef.current)
      mapInstance.current.fitBounds(group.getBounds().pad(0.2))
    }
  }, [location, stores])

  const handleCitySearch = (e) => {
    e.preventDefault()
    if (cityInput.trim()) searchByCity(cityInput.trim())
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 'var(--sp-6)' }}>
        <p className="section-label">Location-Based Intelligence</p>
        <h2 style={{ color: 'var(--green-900)' }}>Nearby Agri Stores</h2>
        <p style={{ color: 'var(--gray-600)', fontSize: '.9rem', marginTop: 'var(--sp-1)' }}>
          Find pesticide and agricultural stores near you using GPS or city search.
        </p>
      </div>

      {/* Location prompt card */}
      {!location && (
        <div className="card" style={{ padding: 'var(--sp-8)' }}>
          <div style={{ textAlign: 'center', marginBottom: 'var(--sp-6)' }}>
            <div style={{ fontSize: 52, marginBottom: 'var(--sp-4)' }}>📍</div>
            <h3 style={{ marginBottom: 'var(--sp-2)', color: 'var(--gray-800)' }}>
              Enable Location
            </h3>
            <p style={{ color: 'var(--gray-500)', fontSize: '.9rem', marginBottom: 'var(--sp-5)' }}>
              We'll find agri stores near you using OpenStreetMap — no data stored.
            </p>
            <button
              className="btn btn-primary btn-lg animate-pulse-green"
              onClick={getLocation}
              disabled={locLoading}
              id="get-location-btn"
            >
              {locLoading
                ? <><span className="spinner" /> Detecting…</>
                : '📍 Use My GPS Location'}
            </button>
          </div>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-3)', margin: 'var(--sp-4) 0' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--gray-200)' }} />
            <span style={{ fontSize: '.8rem', color: 'var(--gray-400)', whiteSpace: 'nowrap' }}>or search by city</span>
            <div style={{ flex: 1, height: 1, background: 'var(--gray-200)' }} />
          </div>

          {/* Manual city search */}
          <form onSubmit={handleCitySearch} style={{ display: 'flex', gap: 'var(--sp-2)' }}>
            <input
              type="text"
              value={cityInput}
              onChange={e => setCityInput(e.target.value)}
              placeholder="e.g. Chennai, Pune, Coimbatore…"
              style={{
                flex: 1,
                padding: '10px 14px',
                border: '1.5px solid var(--gray-300)',
                borderRadius: 'var(--radius-md)',
                fontSize: '.95rem',
                outline: 'none',
                transition: 'border-color .2s',
              }}
              onFocus={e => e.target.style.borderColor = 'var(--green-500)'}
              onBlur={e => e.target.style.borderColor = 'var(--gray-300)'}
              id="city-search-input"
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={locLoading || !cityInput.trim()}
              id="city-search-btn"
            >
              {locLoading ? <span className="spinner" /> : '🔍 Search'}
            </button>
          </form>

          {locError && (
            <div className="alert alert-warning" style={{ marginTop: 'var(--sp-4)' }}>
              <span>⚠️</span><span>{locError}</span>
            </div>
          )}
        </div>
      )}

      {/* Loading */}
      {location && loading && (
        <div className="card" style={{ textAlign: 'center', padding: 'var(--sp-10)' }}>
          <span className="spinner spinner-green" style={{ width: 36, height: 36, borderWidth: 4 }} />
          <p style={{ marginTop: 'var(--sp-4)', color: 'var(--gray-600)' }}>
            Searching stores near <b>{location.city}</b>…
          </p>
        </div>
      )}

      {/* Results */}
      {location && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-5)' }}>

          {/* Status bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--sp-3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-2)' }}>
              <span style={{ fontSize: '.88rem', color: 'var(--gray-600)' }}>
                📍 {location.city} &nbsp;·&nbsp; {stores.length} stores found
              </span>
              {isDemo && (
                <span className="badge badge-yellow">Demo Data</span>
              )}
              {!isDemo && (
                <span className="badge badge-green">Live Data</span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => {
                setCityInput('')
                // Clear location to show search card again — handled via re-search
                searchByCity(location.city)
              }}>
                🔄 Refresh
              </button>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  // Allow user to change location
                  window.location.reload()
                }}
                style={{ fontSize: '.8rem' }}
              >
                📍 Change Location
              </button>
            </div>
          </div>

          {/* Map */}
          <div
            ref={mapRef}
            style={{
              height: 320,
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
              border: '1px solid var(--gray-200)',
              boxShadow: 'var(--shadow-sm)',
              background: 'var(--gray-100)',
            }}
          />

          {/* Alerts */}
          {error && (
            <div className="alert alert-danger"><span>⚠️</span><span>{error}</span></div>
          )}

          {isDemo && (
            <div className="alert alert-warning">
              <span>ℹ️</span>
              <span>
                No agri stores found on OpenStreetMap within 25 km of <b>{location.city}</b>.
                Showing example stores. You can also{' '}
                <a
                  href={`https://www.google.com/maps/search/agricultural+store+near+${encodeURIComponent(location.city)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: 'var(--green-700)', fontWeight: 600 }}
                >
                  search Google Maps
                </a>.
              </span>
            </div>
          )}

          {/* Store list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
            {stores.map(store => (
              <div key={store.id} className="card" style={{ padding: 'var(--sp-4)', display: 'flex', gap: 'var(--sp-4)', alignItems: 'center' }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 'var(--radius-md)',
                  background: 'var(--green-50)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0,
                }}>🏪</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontWeight: 600, color: 'var(--gray-900)', fontSize: '.95rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {store.name}
                  </p>
                  <p style={{ fontSize: '.8rem', color: 'var(--gray-500)', marginTop: 2 }}>
                    {store.address}
                  </p>
                  <div style={{ display: 'flex', gap: 'var(--sp-3)', marginTop: 4, flexWrap: 'wrap' }}>
                    <span className="badge badge-green">📏 {store.distance_km} km</span>
                    {store.phone !== 'Not available' && (
                      <span className="badge badge-gray">📞 {store.phone}</span>
                    )}
                  </div>
                </div>
                <a
                  href={store.directions_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary btn-sm"
                  style={{ flexShrink: 0, textDecoration: 'none' }}
                >
                  🗺️ Directions
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
