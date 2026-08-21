import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import HomePage from './pages/HomePage.jsx'
import ScanPage from './pages/ScanPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import DiseaseGuidePage from './pages/DiseaseGuidePage.jsx'
import AboutPage from './pages/AboutPage.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import './index.css'

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flexGrow: 1 }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/scan" element={<ScanPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/disease-guide" element={<DiseaseGuidePage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

