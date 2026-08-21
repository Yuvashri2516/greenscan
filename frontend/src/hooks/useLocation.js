// src/hooks/useLocation.js – Browser Geolocation Hook with manual fallback
import { useState, useCallback } from 'react'

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org'

export function useLocation() {
  const [location, setLocation] = useState(null)   // { lat, lon, city }
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  /** Reverse-geocode coords → city name */
  async function reverseGeocode(lat, lon) {
    try {
      const r = await fetch(
        `${NOMINATIM_BASE}/reverse?lat=${lat}&lon=${lon}&format=json`,
        { headers: { 'Accept-Language': 'en' } }
      )
      const data = await r.json()
      return (
        data.address?.city ||
        data.address?.town ||
        data.address?.village ||
        data.address?.county ||
        'Your Location'
      )
    } catch (_) {
      return 'Your Location'
    }
  }

  /** Forward-geocode a city name → { lat, lon, city } */
  const searchByCity = useCallback(async (cityName) => {
    if (!cityName?.trim()) return
    setLoading(true)
    setError(null)
    try {
      const r = await fetch(
        `${NOMINATIM_BASE}/search?q=${encodeURIComponent(cityName)}&format=json&limit=1`,
        { headers: { 'Accept-Language': 'en' } }
      )
      const results = await r.json()
      if (!results.length) {
        setError(`Could not find "${cityName}". Try a different city name.`)
        setLoading(false)
        return
      }
      const { lat, lon, display_name } = results[0]
      const city = display_name.split(',')[0].trim()
      setLocation({ lat: parseFloat(lat), lon: parseFloat(lon), city })
    } catch (e) {
      setError('Failed to search city. Check your internet connection.')
    } finally {
      setLoading(false)
    }
  }, [])

  /** GPS-based location detection */
  const getLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.')
      return
    }
    setLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude: lat, longitude: lon } = pos.coords
        const city = await reverseGeocode(lat, lon)
        setLocation({ lat, lon, city })
        setLoading(false)
      },
      (err) => {
        const messages = {
          1: 'Location access denied. Please allow location in your browser, or type your city below.',
          2: 'Location unavailable. Please type your city name below.',
          3: 'Location request timed out. Please try again or type your city below.',
        }
        setError(messages[err.code] || 'Failed to get location. Please type your city below.')
        setLoading(false)
      },
      { timeout: 10000, enableHighAccuracy: false }
    )
  }, [])

  return { location, loading, error, getLocation, searchByCity, setLocation }
}
