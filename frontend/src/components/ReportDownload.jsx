// src/components/ReportDownload.jsx
export default function ReportDownload({ result }) {
  if (!result) return null

  const handleDownload = () => {
    const {
      display_name, confidence, is_healthy, severity, spread_rate,
      disease_info, gsa_metrics, recommendations, progression
    } = result

    const timestamp = new Date().toLocaleString('en-IN', {
      hour12: true, year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
    const gsa = gsa_metrics || {}
    const phs = gsa.plant_health_score ?? 'N/A'
    const affectedPct = gsa.attention_affected_region_percent ?? gsa.affected_area_pct ?? 'N/A'
    const sevLevel = gsa.severity_level || 'N/A'
    const priority = gsa.treatment_priority || 'N/A'
    const weightedAct = gsa.weighted_model_activation ?? gsa.weighted_activation_score ?? 'N/A'

    // Colour coding
    const healthColor = is_healthy
      ? '#16a34a'
      : phs >= 70 ? '#ca8a04' : phs >= 40 ? '#ea580c' : '#dc2626'
    const statusBadge = is_healthy ? '#dcfce7' : '#fee2e2'
    const statusText  = is_healthy ? '#166534' : '#991b1b'

    // Section builder
    const listItems = (arr) =>
      arr?.length
        ? arr.map(i => `<li>${i}</li>`).join('')
        : '<li style="color:#9ca3af">Not available</li>'

    const section = (icon, title, content) => `
      <div class="section">
        <h3>${icon} ${title}</h3>
        ${content}
      </div>`

    // Recommendations
    const rec = recommendations || {}
    const recSections = [
      rec.preventive?.length  ? section('🛡️', 'Preventive Measures',        `<ul>${listItems(rec.preventive)}</ul>`)  : '',
      rec.organic?.length     ? section('🌿', 'Organic Treatment Options',   `<ul>${listItems(rec.organic)}</ul>`)     : '',
      rec.chemical?.length    ? section('🧪', 'Chemical Treatment Options',  `<ul>${listItems(rec.chemical)}</ul>`)    : '',
    ].filter(Boolean).join('')

    // Disease info
    const di = disease_info || {}
    const diSections = [
      di.description            ? section('📖', 'About This Disease',   `<p>${di.description}</p>`)                        : '',
      di.symptoms?.length       ? section('🔍', 'Observed Symptoms',    `<ul>${listItems(di.symptoms)}</ul>`)               : '',
      di.causes?.length         ? section('⚠️', 'Root Causes',          `<ul>${listItems(di.causes)}</ul>`)                 : '',
      di.prevention?.length     ? section('🛡️', 'Prevention Guide',     `<ul>${listItems(di.prevention)}</ul>`)             : '',
      di.organic_solutions?.length  ? section('🌿', 'Organic Remedies', `<ul>${listItems(di.organic_solutions)}</ul>`)      : '',
      di.chemical_solutions?.length ? section('🧪', 'Chemical Remedies',`<ul>${listItems(di.chemical_solutions)}</ul>`)     : '',
    ].filter(Boolean).join('')

    // Progression
    const prog = progression || {}
    const progSection = (prog.risk_level || prog.current_severity_pct != null) ? `
      <div class="section">
        <h3>📈 Disease Progression Forecast (7-Day)</h3>
        <table>
          <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
          <tbody>
            <tr><td>Risk Level</td><td>${prog.risk_level || 'N/A'}</td></tr>
            <tr><td>Current Spread</td><td>${prog.current_severity_pct != null ? prog.current_severity_pct.toFixed(1) + '%' : 'N/A'}</td></tr>
            <tr><td>Projected Spread (7 days)</td><td>${prog.projected_severity_pct != null ? prog.projected_severity_pct.toFixed(1) + '%' : 'N/A'}</td></tr>
            <tr><td>Spread Rate</td><td>${spread_rate || di.spread_rate || 'N/A'}</td></tr>
          </tbody>
        </table>
      </div>` : ''

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GreenScan Report — ${display_name || 'Plant Diagnostic'}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: #f0fdf4;
      color: #1f2937;
      line-height: 1.6;
      padding: 40px 16px 80px;
    }
    .container { max-width: 800px; margin: 0 auto; }

    /* Header */
    .header {
      background: linear-gradient(135deg, #14532d 0%, #166534 60%, #15803d 100%);
      color: white;
      border-radius: 16px;
      padding: 36px 40px;
      margin-bottom: 28px;
      position: relative;
      overflow: hidden;
    }
    .header::before {
      content: '';
      position: absolute;
      top: -40px; right: -40px;
      width: 180px; height: 180px;
      background: rgba(255,255,255,0.06);
      border-radius: 50%;
    }
    .header-logo {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
    }
    .header-logo .leaf { font-size: 2rem; }
    .header-logo h1 { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }
    .header-logo span { font-size: 0.8rem; opacity: 0.7; display: block; font-weight: 400; }
    .header-meta { font-size: 0.78rem; opacity: 0.65; margin-top: 8px; }

    /* Status Banner */
    .status-banner {
      background: ${statusBadge};
      border: 2px solid ${healthColor};
      border-radius: 12px;
      padding: 20px 28px;
      margin-bottom: 28px;
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }
    .status-icon { font-size: 2.4rem; }
    .status-info h2 { font-size: 1.4rem; font-weight: 800; color: ${statusText}; }
    .status-info p { font-size: 0.88rem; color: ${statusText}; opacity: 0.85; margin-top: 2px; }
    .confidence-badge {
      margin-left: auto;
      background: ${healthColor};
      color: white;
      border-radius: 8px;
      padding: 8px 16px;
      font-weight: 700;
      font-size: 1rem;
      white-space: nowrap;
    }

    /* Metrics Grid */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }
    .metric-card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 20px 18px;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card .value {
      font-size: 2rem;
      font-weight: 800;
      color: ${healthColor};
      line-height: 1;
    }
    .metric-card .label {
      font-size: 0.72rem;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-top: 6px;
      font-weight: 600;
    }

    /* Sections */
    .section {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 24px 28px;
      margin-bottom: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .section h3 {
      font-size: 0.92rem;
      font-weight: 700;
      color: #14532d;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 2px solid #dcfce7;
    }
    .section p {
      font-size: 0.88rem;
      color: #374151;
      line-height: 1.7;
    }
    .section ul {
      padding-left: 20px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .section li {
      font-size: 0.88rem;
      color: #374151;
      line-height: 1.6;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.87rem;
    }
    th, td {
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid #f3f4f6;
    }
    th {
      background: #f0fdf4;
      font-weight: 700;
      color: #14532d;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #fafafa; }

    /* Footer */
    .footer {
      text-align: center;
      margin-top: 40px;
      padding: 24px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      font-size: 0.78rem;
      color: #9ca3af;
    }
    .footer strong { color: #374151; }
    .disclaimer {
      background: #fffbeb;
      border: 1px solid #fcd34d;
      border-radius: 10px;
      padding: 14px 20px;
      font-size: 0.8rem;
      color: #78350f;
      margin-top: 20px;
      line-height: 1.6;
    }

    @media print {
      body { background: white; padding: 0; }
      .header { background: #14532d !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
  </style>
</head>
<body>
  <div class="container">

    <!-- Header -->
    <div class="header">
      <div class="header-logo">
        <span class="leaf">🌿</span>
        <div>
          <h1>GreenScan<sup style="font-size:0.6em">+</sup></h1>
          <span>Advanced Agricultural AI — Plant Health Diagnostic Report</span>
        </div>
      </div>
      <div class="header-meta">Generated: ${timestamp}</div>
    </div>

    <!-- Status -->
    <div class="status-banner">
      <div class="status-icon">${is_healthy ? '✅' : '🔴'}</div>
      <div class="status-info">
        <h2>${display_name || 'Unknown'}</h2>
        <p>${is_healthy ? 'No active disease detected. Leaf appears healthy.' : 'Disease detected. Review recommendations below.'}</p>
      </div>
      <div class="confidence-badge">
        ${confidence != null ? confidence.toFixed(1) : 'N/A'}% Confidence
      </div>
    </div>

    <!-- Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="value">${typeof phs === 'number' ? phs : phs}</div>
        <div class="label">Plant Health Score / 100</div>
      </div>
      <div class="metric-card">
        <div class="value">${typeof affectedPct === 'number' ? affectedPct.toFixed(1) + '%' : affectedPct}</div>
        <div class="label">Attention-Affected Region</div>
      </div>
      <div class="metric-card">
        <div class="value">${sevLevel}</div>
        <div class="label">Severity Level</div>
      </div>
      <div class="metric-card">
        <div class="value">${priority}</div>
        <div class="label">Treatment Priority</div>
      </div>
    </div>

    <!-- AI Analysis Table -->
    <div class="section">
      <h3>🤖 AI Spatial Analysis Metrics</h3>
      <table>
        <thead><tr><th>Metric</th><th>Value</th></tr></thead>
        <tbody>
          <tr><td>Plant Health Score (PHS)</td><td>${phs} / 100</td></tr>
          <tr><td>Severity Level</td><td>${sevLevel}</td></tr>
          <tr><td>Attention-Affected Region</td><td>${typeof affectedPct === 'number' ? affectedPct.toFixed(2) + '%' : affectedPct}</td></tr>
          <tr><td>Weighted Model Activation</td><td>${typeof weightedAct === 'number' ? weightedAct.toFixed(4) : weightedAct}</td></tr>
          <tr><td>Treatment Priority</td><td>${priority}</td></tr>
          <tr><td>Traffic Light Status</td><td>${gsa.traffic_light || 'N/A'}</td></tr>
          <tr><td>Risk Level</td><td>${gsa.risk_level || 'N/A'}</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Disease Info sections -->
    ${diSections}

    <!-- Progression -->
    ${progSection}

    <!-- Recommendations -->
    ${recSections}

    <!-- Disclaimer + Footer -->
    <div class="disclaimer">
      ⚠️ <strong>Important Disclaimer:</strong> This report is generated by an AI model and is intended for educational and advisory purposes only. Severity scores are estimated using spatial attention maps, not physical lesion measurements. Always consult a certified agronomist or plant pathologist before applying any treatment.
    </div>

    <div class="footer">
      <strong>GreenScan+ Plant AI</strong> — Powered by EfficientNet-B0 &amp; Grad-CAM Explainability<br>
      Report generated on ${timestamp}
    </div>

  </div>
</body>
</html>`

    const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `GreenScan_Report_${(display_name || 'Report').replace(/\s+/g, '_')}_${Date.now()}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{
      background: '#fff',
      border: '1px solid var(--gray-200)',
      borderRadius: 'var(--radius-md)',
      padding: '16px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
    }}>
      <div>
        <p style={{ margin: 0, fontWeight: 700, color: 'var(--gray-800)', fontSize: '0.9rem' }}>
          📄 Diagnostic Report Ready
        </p>
        <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--gray-500)' }}>
          Opens directly in your browser — double-click to view
        </p>
      </div>
      <button
        className="btn btn-secondary"
        onClick={handleDownload}
        id="download-report-btn"
        title="Download your plant health report as an HTML file"
        style={{ whiteSpace: 'nowrap', flexShrink: 0 }}
      >
        📥 Download Report
      </button>
    </div>
  )
}
