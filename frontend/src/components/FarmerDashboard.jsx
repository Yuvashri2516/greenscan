import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart2, TrendingUp, TrendingDown, Minus, User, Leaf, AlertTriangle, ArrowRight, RefreshCw } from "lucide-react";
import { getFarmerProfile, getFarmerTrends, getFarmerHistory } from "../api/index.js";

export default function FarmerDashboard() {
  const navigate = useNavigate();
  const [farmer, setFarmer] = useState(null);
  const [trends, setTrends] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const farmerId = localStorage.getItem("greenscan_farmer_id");

  useEffect(() => {
    if (!farmerId) {
      setLoading(false);
      return;
    }
    loadData();
  }, [farmerId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [farmerRes, trendsRes, historyRes] = await Promise.all([
        getFarmerProfile(farmerId),
        getFarmerTrends(farmerId),
        getFarmerHistory(farmerId, 10)
      ]);
      setFarmer(farmerRes.farmer);
      setTrends(trendsRes.trends);
      setHistory(historyRes.history || []);
    } catch (err) {
      setError("Failed to load dashboard. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  // No profile
  if (!farmerId) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg-primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center", maxWidth: 420 }}>
          <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🌱</div>
          <h2 style={{ color: "var(--text-primary)", marginBottom: "0.75rem" }}>No Profile Found</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>
            Create a farmer profile to see your personalized dashboard, scan history, and crop health trends.
          </p>
          <button
            onClick={() => navigate("/profile")}
            style={{
              display: "inline-flex", alignItems: "center", gap: "0.5rem",
              background: "linear-gradient(135deg, var(--primary-green), var(--accent-cyan))",
              border: "none", borderRadius: 12, color: "white",
              padding: "0.85rem 2rem", fontSize: "1rem", fontWeight: 700, cursor: "pointer",
              boxShadow: "0 4px 20px rgba(16,185,129,0.4)"
            }}>
            Create Profile <ArrowRight size={18} />
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg-primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 48, height: 48, border: "3px solid rgba(16,185,129,0.2)", borderTop: "3px solid var(--primary-green)", borderRadius: "50%", animation: "spin 1s linear infinite", margin: "0 auto 1rem" }} />
          <div style={{ color: "var(--text-secondary)" }}>Loading dashboard...</div>
        </div>
      </div>
    );
  }

  const trendIcon = {
    "improving": <TrendingUp size={18} color="var(--primary-green)" />,
    "worsening": <TrendingDown size={18} color="#ef4444" />,
    "stable": <Minus size={18} color="#f59e0b" />,
    "insufficient_data": <BarChart2 size={18} color="var(--text-secondary)" />
  };

  const trendLabel = {
    "improving": { label: "↑ Improving", color: "var(--primary-green)", bg: "rgba(16,185,129,0.1)" },
    "worsening": { label: "↓ Worsening", color: "#ef4444", bg: "rgba(239,68,68,0.1)" },
    "stable": { label: "→ Stable", color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
    "insufficient_data": { label: "Needs more scans", color: "var(--text-secondary)", bg: "rgba(255,255,255,0.05)" }
  };

  const trend = trends?.trend_direction || "insufficient_data";
  const tl = trendLabel[trend] || trendLabel.insufficient_data;

  const lastScan = history[0];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "2rem 1rem" }}>
      <div style={{ maxWidth: 900, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h1 style={{ color: "var(--text-primary)", fontSize: "1.8rem", fontWeight: 700, margin: 0 }}>
              Farm Dashboard
            </h1>
            {farmer && (
              <p style={{ color: "var(--text-secondary)", marginTop: "0.4rem" }}>
                <User size={14} style={{ verticalAlign: "middle", marginRight: "0.3rem" }} />
                {farmer.name}
                {farmer.farm_name && ` · ${farmer.farm_name}`}
                {farmer.crop_stage && ` · ${farmer.crop_stage} stage`}
                {farmer.farm_location && ` · ${farmer.farm_location}`}
              </p>
            )}
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button onClick={loadData} title="Refresh" style={{ background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-color)", borderRadius: 10, padding: "0.6rem 1rem", color: "var(--text-secondary)", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.85rem" }}>
              <RefreshCw size={15} /> Refresh
            </button>
            <button onClick={() => navigate("/profile")} style={{ background: "rgba(16,185,129,0.1)", border: "1px solid var(--primary-green)", borderRadius: 10, padding: "0.6rem 1rem", color: "var(--primary-green)", cursor: "pointer", fontSize: "0.85rem", fontWeight: 600 }}>
              Edit Profile
            </button>
          </div>
        </div>

        {error && (
          <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: "1rem", color: "#ef4444", marginBottom: "1.5rem" }}>
            {error}
          </div>
        )}

        {/* Stats Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
          <StatCard
            label="Total Scans"
            value={trends?.scan_count ?? 0}
            icon={<Leaf size={22} color="var(--primary-green)" />}
            color="var(--primary-green)"
          />
          <StatCard
            label="Avg Health Score"
            value={trends?.avg_health_score != null ? `${trends.avg_health_score}/100` : "—"}
            icon={<BarChart2 size={22} color="var(--accent-cyan)" />}
            color="var(--accent-cyan)"
          />
          <StatCard
            label="Health Trend"
            value={<span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>{trendIcon[trend]}{tl.label}</span>}
            icon={trendIcon[trend]}
            color={tl.color}
            bg={tl.bg}
          />
          {lastScan && (
            <StatCard
              label="Last Diagnosis"
              value={lastScan.display_name}
              sub={`${lastScan.confidence?.toFixed(1)}% confidence · ${new Date(lastScan.timestamp).toLocaleDateString()}`}
              icon={<AlertTriangle size={22} color="#f59e0b" />}
              color="#f59e0b"
            />
          )}
        </div>

        {/* Health Score Sparkline */}
        {trends?.health_scores?.length > 1 && (
          <div style={{
            background: "var(--bg-card)", borderRadius: 18,
            border: "1px solid var(--border-color)", padding: "1.5rem",
            marginBottom: "1.5rem"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <BarChart2 size={16} color="var(--primary-green)" />
              <span style={{ color: "var(--text-primary)", fontWeight: 700 }}>Plant Health Score Over Time</span>
              <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>(last {trends.health_scores.length} scans)</span>
            </div>
            <Sparkline data={trends.health_scores.map(([, v]) => v)} color="var(--primary-green)" max={100} />
          </div>
        )}

        {/* Scan History Table */}
        {history.length > 0 && (
          <div style={{ background: "var(--bg-card)", borderRadius: 18, border: "1px solid var(--border-color)", overflow: "hidden", marginBottom: "1.5rem" }}>
            <div style={{ padding: "1.1rem 1.5rem", borderBottom: "1px solid var(--border-color)" }}>
              <span style={{ color: "var(--text-primary)", fontWeight: 700 }}>Recent Scans</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.87rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
                    {["Date", "Diagnosis", "Confidence", "PHS", "Severity"].map(h => (
                      <th key={h} style={{ padding: "0.75rem 1rem", color: "var(--text-secondary)", fontWeight: 600, textAlign: "left" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.map((scan, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--text-secondary)" }}>{new Date(scan.timestamp).toLocaleDateString()}</td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--text-primary)", fontWeight: 500 }}>{scan.display_name}</td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--text-secondary)" }}>{scan.confidence?.toFixed(1)}%</td>
                      <td style={{ padding: "0.75rem 1rem" }}>
                        <span style={{
                          background: healthScoreColor(scan.plant_health_score).bg,
                          color: healthScoreColor(scan.plant_health_score).color,
                          padding: "0.2rem 0.5rem", borderRadius: 6, fontWeight: 600, fontSize: "0.82rem"
                        }}>
                          {scan.plant_health_score}/100
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem 1rem", color: severityColor(scan.severity_level) }}>{scan.severity_level}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* CTA if no history */}
        {history.length === 0 && !loading && (
          <div style={{ textAlign: "center", padding: "3rem", background: "var(--bg-card)", borderRadius: 18, border: "1px solid var(--border-color)" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📷</div>
            <h3 style={{ color: "var(--text-primary)", marginBottom: "0.75rem" }}>No Scans Yet</h3>
            <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>Scan your tomato leaves to start building your crop health history.</p>
            <button onClick={() => navigate("/scan")} style={{ background: "linear-gradient(135deg, var(--primary-green), var(--accent-cyan))", border: "none", borderRadius: 12, color: "white", padding: "0.85rem 2rem", fontSize: "1rem", fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 20px rgba(16,185,129,0.4)" }}>
              Scan Now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, icon, color, bg }) {
  return (
    <div style={{
      background: bg || "var(--bg-card)", borderRadius: 16,
      border: "1px solid var(--border-color)", padding: "1.25rem",
    }}>
      <div style={{ color: "var(--text-secondary)", fontSize: "0.78rem", fontWeight: 600, marginBottom: "0.5rem", textTransform: "uppercase" }}>{label}</div>
      <div style={{ color: color || "var(--text-primary)", fontSize: "1.3rem", fontWeight: 700 }}>{value}</div>
      {sub && <div style={{ color: "var(--text-secondary)", fontSize: "0.78rem", marginTop: "0.3rem" }}>{sub}</div>}
    </div>
  );
}

function Sparkline({ data, color, max = 100 }) {
  if (!data || data.length < 2) return null;
  const W = 600, H = 80, pad = 8;
  const minVal = Math.min(...data);
  const maxVal = Math.max(max, ...data);
  const range = maxVal - minVal || 1;

  const pts = data.map((v, i) => {
    const x = pad + (i / (data.length - 1)) * (W - 2 * pad);
    const y = H - pad - ((v - minVal) / range) * (H - 2 * pad);
    return `${x},${y}`;
  });

  const pathD = `M ${pts.join(" L ")}`;
  const areaD = `M ${pts[0]} L ${pts.join(" L ")} L ${W - pad},${H - pad} L ${pad},${H - pad} Z`;

  return (
    <div style={{ overflowX: "auto" }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, height: H, display: "block" }}>
        <defs>
          <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        <path d={areaD} fill="url(#sparkGrad)" />
        <path d={pathD} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        {data.map((v, i) => {
          const [x, y] = pts[i].split(",").map(Number);
          return <circle key={i} cx={x} cy={y} r="4" fill={color} opacity={0.9} />;
        })}
      </svg>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
        <span>Oldest</span>
        <span>Latest</span>
      </div>
    </div>
  );
}

function healthScoreColor(score) {
  if (score >= 75) return { color: "var(--primary-green)", bg: "rgba(16,185,129,0.1)" };
  if (score >= 50) return { color: "#f59e0b", bg: "rgba(245,158,11,0.1)" };
  return { color: "#ef4444", bg: "rgba(239,68,68,0.1)" };
}

function severityColor(severity) {
  return { Healthy: "var(--primary-green)", Mild: "#f59e0b", Moderate: "#f97316", Severe: "#ef4444" }[severity] || "var(--text-secondary)";
}
