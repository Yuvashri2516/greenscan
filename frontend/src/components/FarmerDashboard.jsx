import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  BarChart2, TrendingUp, TrendingDown, Minus, User, Leaf, 
  AlertTriangle, ArrowRight, RefreshCw, Camera, Activity, Edit3,
  MessageSquare, Star, CheckCircle2, Send
} from "lucide-react";
import { getFarmerProfile, getFarmerTrends, getFarmerHistory, submitFeedback } from "../api/index.js";

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

  // No profile state
  if (!farmerId) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--green-50)", display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem 1rem" }}>
        <div style={{ textAlign: "center", maxWidth: 440, background: "var(--white)", padding: "2.5rem 2rem", borderRadius: 16, border: "1.5px solid var(--gray-200)", boxShadow: "var(--shadow-card)" }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--green-100)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.25rem" }}>
            <Leaf size={32} color="var(--green-700)" />
          </div>
          <h2 style={{ color: "var(--gray-900)", fontSize: "1.5rem", fontWeight: 800, marginBottom: "0.75rem" }}>No Profile Found</h2>
          <p style={{ color: "var(--gray-600)", fontSize: "0.95rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
            Create a farmer profile to see your personalized dashboard, scan history, and crop health trends.
          </p>
          <button
            onClick={() => navigate("/profile")}
            style={{
              display: "inline-flex", alignItems: "center", gap: "0.5rem",
              background: "var(--green-700)", border: "none", borderRadius: 10, color: "white",
              padding: "0.85rem 1.75rem", fontSize: "0.95rem", fontWeight: 700, cursor: "pointer",
              boxShadow: "0 4px 14px rgba(27,143,58,0.35)", transition: "all 0.2s"
            }}>
            Create Profile <ArrowRight size={18} />
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--green-50)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 48, height: 48, border: "3px solid var(--gray-200)", borderTop: "3px solid var(--green-700)", borderRadius: "50%", animation: "spin 1s linear infinite", margin: "0 auto 1rem" }} />
          <div style={{ color: "var(--gray-600)", fontWeight: 600 }}>Loading farm dashboard...</div>
        </div>
      </div>
    );
  }

  const trendIcon = {
    "improving": <TrendingUp size={18} color="var(--green-700)" />,
    "worsening": <TrendingDown size={18} color="var(--accent-red)" />,
    "stable": <Minus size={18} color="var(--accent-orange)" />,
    "insufficient_data": <Activity size={18} color="var(--gray-500)" />
  };

  const trendLabel = {
    "improving": { label: "↑ Improving", color: "var(--green-800)", bg: "var(--green-100)" },
    "worsening": { label: "↓ Worsening", color: "var(--accent-red)", bg: "#fef2f2" },
    "stable": { label: "→ Stable", color: "var(--accent-orange)", bg: "#fffbeb" },
    "insufficient_data": { label: "Needs more scans", color: "var(--gray-600)", bg: "var(--gray-100)" }
  };

  const trend = trends?.trend_direction || "insufficient_data";
  const tl = trendLabel[trend] || trendLabel.insufficient_data;

  const subtitleInfo = farmer ? [
    farmer.name,
    farmer.farm_name,
    farmer.crop_stage && `${farmer.crop_stage} stage`,
    farmer.farm_location
  ].filter(Boolean).join(" • ") : "";

  const lastScan = history[0];

  return (
    <div style={{ minHeight: "100vh", background: "var(--green-50)", padding: "2.5rem 1.5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", flexWrap: "wrap", gap: "1.25rem" }}>
          <div>
            <h1 style={{ color: "var(--gray-900)", fontSize: "1.85rem", fontWeight: 800, margin: 0, letterSpacing: "-0.02em" }}>
              Farm Dashboard
            </h1>
            {subtitleInfo && (
              <p style={{ color: "var(--gray-700)", marginTop: "0.4rem", fontSize: "0.92rem", fontWeight: 500 }}>
                {subtitleInfo}
              </p>
            )}
          </div>
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <button 
              onClick={loadData} 
              title="Refresh Dashboard" 
              style={{ 
                background: "var(--white)", border: "1.5px solid var(--gray-200)", 
                borderRadius: 10, padding: "0.65rem 1.1rem", color: "var(--gray-800)", 
                cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.5rem", 
                fontSize: "0.88rem", fontWeight: 600, transition: "all 0.2s" 
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = "var(--gray-400)"}
              onMouseLeave={e => e.currentTarget.style.borderColor = "var(--gray-200)"}
            >
              <RefreshCw size={15} /> Refresh
            </button>
            <button 
              onClick={() => navigate("/profile")} 
              style={{ 
                background: "var(--green-100)", border: "1.5px solid var(--green-200)", 
                borderRadius: 10, padding: "0.65rem 1.1rem", color: "var(--green-800)", 
                cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.5rem", 
                fontSize: "0.88rem", fontWeight: 700, transition: "all 0.2s" 
              }}
              onMouseEnter={e => e.currentTarget.style.background = "var(--green-200)"}
              onMouseLeave={e => e.currentTarget.style.background = "var(--green-100)"}
            >
              <Edit3 size={15} /> Edit Profile
            </button>
          </div>
        </div>

        {error && (
          <div style={{ background: "#fef2f2", border: "1.5px solid #fecaca", borderRadius: 12, padding: "1rem 1.25rem", color: "var(--accent-red)", fontWeight: 600, marginBottom: "1.75rem" }}>
            {error}
          </div>
        )}

        {/* 3 Metric Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem", marginBottom: "1.75rem" }}>
          <MetricCard
            icon={<Leaf size={20} color="var(--green-700)" />}
            label="TOTAL SCANS"
            value={trends?.scan_count ?? 0}
            sub={trends?.scan_count > 0 ? "Scans recorded to date" : "No scans recorded"}
          />
          <MetricCard
            icon={<BarChart2 size={20} color="var(--green-700)" />}
            label="AVG HEALTH SCORE"
            value={trends?.avg_health_score != null ? `${trends.avg_health_score}/100` : "—"}
            sub={trends?.avg_health_score != null ? (trends.avg_health_score >= 75 ? "Optimal plant condition" : "Requires active monitoring") : "No score calculated"}
          />
          <MetricCard
            icon={<Activity size={20} color="var(--green-700)" />}
            label="HEALTH TREND"
            value={
              <span style={{ 
                display: "inline-flex", alignItems: "center", gap: "0.4rem", 
                background: tl.bg, color: tl.color, padding: "0.25rem 0.65rem", 
                borderRadius: 8, fontSize: "1.1rem", fontWeight: 700 
              }}>
                {trendIcon[trend]} {tl.label}
              </span>
            }
            sub={trend === "insufficient_data" ? "Requires multiple scan logs" : "Calculated from scan history"}
          />
        </div>

        {/* Empty State Card (No Scans) */}
        {history.length === 0 && !loading && (
          <div style={{ 
            background: "var(--white)", borderRadius: 16, 
            border: "1.5px solid var(--gray-200)", padding: "2.75rem 2rem", 
            textAlign: "center", boxShadow: "var(--shadow-card)", marginTop: "0.5rem" 
          }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--green-100)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.25rem" }}>
              <Camera size={30} color="var(--green-700)" />
            </div>
            <h3 style={{ color: "var(--gray-900)", fontSize: "1.35rem", fontWeight: 800, marginBottom: "0.5rem" }}>
              No Scans Yet
            </h3>
            <p style={{ color: "var(--gray-600)", fontSize: "0.95rem", maxWidth: 420, margin: "0 auto 1.75rem", lineHeight: 1.5 }}>
              Scan your tomato leaves to start building your crop health history and AI diagnostics.
            </p>
            <button 
              onClick={() => navigate("/scan")} 
              style={{ 
                background: "var(--green-700)", border: "none", borderRadius: 10, 
                color: "#ffffff", padding: "0.85rem 2.25rem", fontSize: "0.95rem", 
                fontWeight: 700, cursor: "pointer", display: "inline-flex", 
                alignItems: "center", gap: "0.6rem", boxShadow: "0 4px 14px rgba(27,143,58,0.35)",
                transition: "all 0.2s"
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = "var(--green-800)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = "var(--green-700)";
                e.currentTarget.style.transform = "none";
              }}
            >
              Scan Now <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* Health Score Sparkline */}
        {trends?.health_scores?.length > 1 && (
          <div style={{
            background: "var(--white)", borderRadius: 16,
            border: "1.5px solid var(--gray-200)", padding: "1.5rem",
            marginBottom: "1.75rem", boxShadow: "var(--shadow-card)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <BarChart2 size={16} color="var(--green-700)" />
              <span style={{ color: "var(--gray-900)", fontWeight: 700, fontSize: "1.05rem" }}>Plant Health Score Over Time</span>
              <span style={{ color: "var(--gray-600)", fontSize: "0.82rem" }}>(last {trends.health_scores.length} scans)</span>
            </div>
            <Sparkline data={trends.health_scores.map(([, v]) => v)} color="var(--green-700)" max={100} />
          </div>
        )}

        {/* Scan History Table */}
        {history.length > 0 && (
          <div style={{ background: "var(--white)", borderRadius: 16, border: "1.5px solid var(--gray-200)", overflow: "hidden", marginBottom: "1.75rem", boxShadow: "var(--shadow-card)" }}>
            <div style={{ padding: "1.1rem 1.5rem", borderBottom: "1.5px solid var(--gray-200)", background: "var(--green-50)" }}>
              <span style={{ color: "var(--gray-900)", fontWeight: 700, fontSize: "1.05rem" }}>Recent Scans</span>
            </div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1.5px solid var(--gray-200)", background: "var(--gray-50)" }}>
                    {["Date", "Diagnosis", "Confidence", "PHS", "Severity"].map(h => (
                      <th key={h} style={{ padding: "0.75rem 1rem", color: "var(--gray-900)", fontWeight: 700, textAlign: "left" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.map((scan, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--gray-200)" }}>
                      <td style={{ padding: "0.85rem 1rem", color: "var(--gray-700)" }}>{new Date(scan.timestamp).toLocaleDateString()}</td>
                      <td style={{ padding: "0.85rem 1rem", color: "var(--gray-900)", fontWeight: 700 }}>{scan.display_name}</td>
                      <td style={{ padding: "0.85rem 1rem", color: "var(--gray-700)" }}>{scan.confidence?.toFixed(1)}%</td>
                      <td style={{ padding: "0.85rem 1rem" }}>
                        <span style={{
                          background: healthScoreColor(scan.plant_health_score).bg,
                          color: healthScoreColor(scan.plant_health_score).color,
                          padding: "0.2rem 0.6rem", borderRadius: 6, fontWeight: 700, fontSize: "0.82rem"
                        }}>
                          {scan.plant_health_score}/100
                        </span>
                      </td>
                      <td style={{ padding: "0.85rem 1rem", color: severityColor(scan.severity_level), fontWeight: 700 }}>{scan.severity_level}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Feedback Section */}
        <FarmerFeedbackSection />

      </div>
    </div>
  );
}

const RATING_LABELS = {
  1: "1 — Not useful",
  2: "2 — Slightly useful",
  3: "3 — Useful",
  4: "4 — Very useful",
  5: "5 — Extremely useful"
};

const CATEGORIES = [
  "Disease Detection",
  "Recommendations",
  "AI Assistant",
  "Dashboard",
  "Mobile App",
  "Website",
  "Weather / Risk Information",
  "Other"
];

function FarmerFeedbackSection() {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [category, setCategory] = useState("");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (rating < 1 || rating > 5) {
      setError("Please select a rating between 1 and 5 stars.");
      return;
    }
    if (!comment.trim() || comment.trim().length < 3) {
      setError("Please enter at least 3 characters of feedback.");
      return;
    }

    setSubmitting(true);
    try {
      const farmerId = localStorage.getItem("greenscan_farmer_id");
      await submitFeedback(rating, comment.trim(), category || null, farmerId || null);
      setSubmitted(true);
      setRating(0);
      setCategory("");
      setComment("");
    } catch (err) {
      setError(err.message || "Failed to submit feedback. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div style={{
        background: "var(--white)",
        borderRadius: 16,
        border: "1.5px solid var(--gray-200)",
        padding: "2.5rem 1.5rem",
        marginBottom: "1.75rem",
        boxShadow: "var(--shadow-card)",
        textAlign: "center"
      }}>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: "50%",
          background: "var(--green-100)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 1.25rem",
          color: "var(--green-700)"
        }}>
          <CheckCircle2 size={32} />
        </div>
        <h3 style={{ color: "var(--gray-900)", fontSize: "1.35rem", fontWeight: 800, marginBottom: "0.5rem" }}>
          Thank you! Your feedback has been submitted.
        </h3>
        <p style={{ color: "var(--gray-600)", fontSize: "0.95rem", maxWidth: 460, margin: "0 auto 1.5rem", lineHeight: 1.5 }}>
          Your feedback helps us improve GreenScan for farmers and growers.
        </p>
        <button
          onClick={() => setSubmitted(false)}
          style={{
            background: "var(--green-700)",
            border: "none",
            borderRadius: 10,
            color: "#ffffff",
            padding: "0.75rem 1.5rem",
            fontSize: "0.9rem",
            fontWeight: 700,
            cursor: "pointer",
            transition: "all 0.2s"
          }}
          onMouseEnter={e => e.currentTarget.style.background = "var(--green-800)"}
          onMouseLeave={e => e.currentTarget.style.background = "var(--green-700)"}
        >
          Submit another response
        </button>
      </div>
    );
  }

  return (
    <div style={{
      background: "var(--white)",
      borderRadius: 16,
      border: "1.5px solid var(--gray-200)",
      padding: "1.75rem 1.5rem",
      marginBottom: "1.75rem",
      boxShadow: "var(--shadow-card)"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.4rem" }}>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: "var(--green-100)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--green-700)" }}>
          <MessageSquare size={18} />
        </div>
        <h3 style={{ color: "var(--gray-900)", fontSize: "1.25rem", fontWeight: 800, margin: 0 }}>
          Share Your Feedback
        </h3>
      </div>
      <p style={{ color: "var(--gray-600)", fontSize: "0.9rem", marginBottom: "1.5rem", marginTop: 0 }}>
        Your feedback helps us improve GreenScan for farmers and growers.
      </p>

      {error && (
        <div style={{ background: "#fef2f2", border: "1.5px solid #fecaca", borderRadius: 10, padding: "0.75rem 1rem", color: "var(--accent-red)", fontSize: "0.88rem", fontWeight: 600, marginBottom: "1.25rem" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Rating + Category Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.25rem", alignItems: "flex-start" }}>
          
          {/* 1-5 Star Rating */}
          <div>
            <label style={{ display: "block", color: "var(--gray-900)", fontWeight: 700, fontSize: "0.9rem", marginBottom: "0.5rem" }}>
              How useful has GreenScan been for you? <span style={{ color: "var(--accent-red)" }}>*</span>
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              {[1, 2, 3, 4, 5].map((star) => {
                const active = star <= (hoverRating || rating);
                return (
                  <button
                    key={star}
                    type="button"
                    aria-label={RATING_LABELS[star]}
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    style={{
                      background: "transparent",
                      border: "none",
                      padding: "4px",
                      cursor: "pointer",
                      color: active ? "#f59e0b" : "#d1d5db",
                      transition: "transform 0.15s ease, color 0.15s ease"
                    }}
                  >
                    <Star size={26} fill={active ? "#f59e0b" : "transparent"} />
                  </button>
                );
              })}
            </div>
            <div style={{ fontSize: "0.82rem", color: (hoverRating || rating) ? "var(--green-800)" : "var(--gray-500)", fontWeight: 600, marginTop: "0.4rem", minHeight: "20px" }}>
              {(hoverRating || rating) ? RATING_LABELS[hoverRating || rating] : "Select a rating (1–5 stars)"}
            </div>
          </div>

          {/* Category Dropdown */}
          <div>
            <label htmlFor="feedback-category" style={{ display: "block", color: "var(--gray-900)", fontWeight: 700, fontSize: "0.9rem", marginBottom: "0.5rem" }}>
              What is your feedback mainly about? <span style={{ color: "var(--gray-500)", fontWeight: 400 }}>(Optional)</span>
            </label>
            <select
              id="feedback-category"
              value={category}
              onChange={e => setCategory(e.target.value)}
              style={{
                width: "100%",
                padding: "0.7rem 0.9rem",
                borderRadius: 10,
                border: "1.5px solid var(--gray-200)",
                background: "var(--white)",
                color: "var(--gray-900)",
                fontSize: "0.9rem",
                fontWeight: 500,
                outline: "none",
                cursor: "pointer",
                transition: "border-color 0.2s"
              }}
              onFocus={e => e.target.style.borderColor = "var(--green-700)"}
              onBlur={e => e.target.style.borderColor = "var(--gray-200)"}
            >
              <option value="">Select a category...</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

        </div>

        {/* Feedback Textarea */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <label htmlFor="feedback-comment" style={{ color: "var(--gray-900)", fontWeight: 700, fontSize: "0.9rem" }}>
              Tell us about your experience <span style={{ color: "var(--accent-red)" }}>*</span>
            </label>
            <span style={{ fontSize: "0.78rem", color: comment.length >= 500 ? "var(--accent-red)" : "var(--gray-500)", fontWeight: 600 }}>
              {comment.length} / 500
            </span>
          </div>
          <textarea
            id="feedback-comment"
            value={comment}
            onChange={e => setComment(e.target.value.slice(0, 500))}
            placeholder="Tell us what worked well, what could be improved, or what you would like GreenScan to add..."
            rows={4}
            maxLength={500}
            style={{
              width: "100%",
              padding: "0.85rem 1rem",
              borderRadius: 10,
              border: "1.5px solid var(--gray-200)",
              background: "var(--white)",
              color: "var(--gray-900)",
              fontSize: "0.92rem",
              lineHeight: 1.5,
              outline: "none",
              resize: "vertical",
              minHeight: "100px",
              transition: "border-color 0.2s, box-shadow 0.2s",
              boxSizing: "border-box"
            }}
            onFocus={e => {
              e.target.style.borderColor = "var(--green-700)";
              e.target.style.boxShadow = "0 0 0 3px rgba(27,143,58,0.12)";
            }}
            onBlur={e => {
              e.target.style.borderColor = "var(--gray-200)";
              e.target.style.boxShadow = "none";
            }}
          />
        </div>

        {/* Submit Button */}
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            type="submit"
            disabled={submitting || rating === 0 || comment.trim().length < 3}
            style={{
              background: (submitting || rating === 0 || comment.trim().length < 3) ? "var(--gray-400)" : "var(--green-700)",
              border: "none",
              borderRadius: 10,
              color: "#ffffff",
              padding: "0.75rem 1.75rem",
              fontSize: "0.92rem",
              fontWeight: 700,
              cursor: (submitting || rating === 0 || comment.trim().length < 3) ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "0.5rem",
              boxShadow: (submitting || rating === 0 || comment.trim().length < 3) ? "none" : "0 4px 14px rgba(27,143,58,0.3)",
              transition: "all 0.2s ease"
            }}
            onMouseEnter={e => {
              if (!submitting && rating > 0 && comment.trim().length >= 3) {
                e.currentTarget.style.background = "var(--green-800)";
              }
            }}
            onMouseLeave={e => {
              if (!submitting && rating > 0 && comment.trim().length >= 3) {
                e.currentTarget.style.background = "var(--green-700)";
              }
            }}
          >
            {submitting ? "Submitting..." : <>Submit Feedback <Send size={16} /></>}
          </button>
        </div>

      </form>
    </div>
  );
}

function MetricCard({ label, value, sub, icon }) {
  return (
    <div style={{
      background: "var(--white)", borderRadius: 16,
      border: "1.5px solid var(--gray-200)", padding: "1.35rem 1.5rem",
      boxShadow: "var(--shadow-card)", display: "flex", flexDirection: "column",
      justifyContent: "space-between", minHeight: "130px"
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <span style={{ color: "var(--gray-600)", fontSize: "0.78rem", fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase" }}>
          {label}
        </span>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: "var(--green-100)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          {icon}
        </div>
      </div>
      <div style={{ color: "var(--gray-900)", fontSize: "1.75rem", fontWeight: 800, lineHeight: 1.2, marginBottom: "0.35rem" }}>
        {value}
      </div>
      {sub && <div style={{ color: "var(--gray-600)", fontSize: "0.82rem", fontWeight: 500 }}>{sub}</div>}
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
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--gray-600)", marginTop: "0.25rem", fontWeight: 600 }}>
        <span>Oldest</span>
        <span>Latest</span>
      </div>
    </div>
  );
}

function healthScoreColor(score) {
  if (score >= 75) return { color: "var(--green-800)", bg: "var(--green-100)" };
  if (score >= 50) return { color: "var(--accent-orange)", bg: "#fffbeb" };
  return { color: "var(--accent-red)", bg: "#fef2f2" };
}

function severityColor(severity) {
  return { Healthy: "var(--green-800)", Mild: "var(--accent-orange)", Moderate: "#d97706", Severe: "var(--accent-red)" }[severity] || "var(--gray-700)";
}
