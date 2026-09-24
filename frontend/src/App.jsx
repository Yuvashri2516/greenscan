import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Navbar from './components/Navbar.jsx'
import HomePage from './pages/HomePage.jsx'
import ScanPage from './pages/ScanPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import DiseaseGuidePage from './pages/DiseaseGuidePage.jsx'
import AboutPage from './pages/AboutPage.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import './index.css'

// GreenScan 2.0: Lazy-loaded new pages
const FarmerProfilePage = lazy(() => import('./pages/FarmerProfilePage.jsx'))
const FarmerDashboard = lazy(() => import('./components/FarmerDashboard.jsx'))

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flexGrow: 1 }}>
            <Suspense fallback={<div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'60vh',color:'var(--text-secondary)',fontSize:'1.1rem'}}>Loading...</div>}>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/scan" element={<ScanPage />} />
                <Route path="/history" element={<HistoryPage />} />
                <Route path="/disease-guide" element={<DiseaseGuidePage />} />
                <Route path="/about" element={<AboutPage />} />
                {/* GreenScan 2.0 */}
                <Route path="/profile" element={<FarmerProfilePage />} />
                <Route path="/dashboard" element={<FarmerDashboard />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
