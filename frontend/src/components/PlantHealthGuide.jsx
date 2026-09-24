import { useState } from "react";
import {
  AlertTriangle, CheckCircle, Shield, Zap, Clock, Eye,
  Leaf, Droplets, ThumbsUp, ChevronDown, ChevronUp, Info
} from "lucide-react";

/**
 * PlantHealthGuide - GreenScan 2.0 Structured Recommendation Panel
 *
 * Renders the structured_recommendation field from /predict response.
 * Falls back gracefully if structured_recommendation is absent.
 */
export default function PlantHealthGuide({ recommendation, validationInfo }) {
  const [treatmentTab, setTreatmentTab] = useState("organic");
  const [expandedSections, setExpandedSections] = useState({ prevention: false, safety: false });

  if (!recommendation) return null;

  const {
    disease_display_name, severity, confidence_pct, urgency, is_healthy,
    treatment_window, immediate_actions = [], prevention = [],
    treatment_options = {}, environmental_actions = [],
    monitoring = {}, safety_information = [],
    personalization_notes = [], history_trend, disclaimer
  } = recommendation;

  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const severityColor = {
    "Healthy": "var(--primary-green)",
    "Mild": "#f59e0b",
    "Moderate": "#f97316",
    "Severe": "#ef4444"
  }[severity] || "var(--primary-green)";

  const urgencyBadge = {
    "None": { bg: "rgba(16,185,129,0.12)", color: "var(--primary-green)", label: "No Action Required" },
    "Low": { bg: "rgba(245,158,11,0.12)", color: "#f59e0b", label: "Low Priority" },
    "Medium": { bg: "rgba(249,115,22,0.12)", color: "#f97316", label: "Treat Within 48h" },
    "High": { bg: "rgba(239,68,68,0.12)", color: "#ef4444", label: "URGENT — Treat Now" }
  }[urgency] || urgencyBadge?.None;

  return (
    <div style={{ display: "grid", gap: "1rem", marginTop: "1.5rem" }}>

      {/* Header: Condition + Urgency */}
      <div style={{
        background: "var(--bg-card)", borderRadius: 16,
        border: `1px solid ${severityColor}44`,
        padding: "1.25rem", display: "flex", flexWrap: "wrap",
        gap: "1rem", alignItems: "center", justifyContent: "space-between"
      }}>
        <div>
          <div style={{ color: "var(--text-secondary)", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
            DIAGNOSIS
          </div>
          <div style={{ color: "var(--text-primary)", fontSize: "1.15rem", fontWeight: 700 }}>
            {disease_display_name}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.4rem" }}>
            <span style={{ color: severityColor, fontSize: "0.9rem", fontWeight: 600 }}>
              ● {severity} Severity
            </span>
            <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              · {confidence_pct}% confidence
            </span>
          </div>
        </div>

        {/* Urgency Badge */}
        {urgencyBadge && (
          <div style={{
            padding: "0.6rem 1.1rem", borderRadius: 10,
            background: urgencyBadge.bg, color: urgencyBadge.color,
            fontWeight: 700, fontSize: "0.85rem", whiteSpace: "nowrap"
          }}>
            {urgencyBadge.label}
          </div>
        )}
      </div>

      {/* Personalization + Trend Notes */}
      {(personalization_notes.length > 0 || history_trend === "worsening" || history_trend === "improving") && (
        <div style={{
          background: "rgba(6,182,212,0.07)", border: "1px solid rgba(6,182,212,0.2)",
          borderRadius: 12, padding: "1rem"
        }}>
          <div style={{ color: "var(--accent-cyan)", fontSize: "0.8rem", fontWeight: 700, marginBottom: "0.5rem" }}>
            <Info size={13} style={{marginRight:"0.35rem",verticalAlign:"middle"}} />
            PERSONALIZED FOR YOUR FARM
          </div>
          {personalization_notes.map((note, i) => (
            <div key={i} style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginBottom: "0.3rem" }}>
              • {note}
            </div>
          ))}
          {history_trend === "worsening" && (
            <div style={{ color: "#f97316", fontSize: "0.88rem", fontWeight: 600, marginTop: "0.35rem" }}>
              ⚠️ Your scan history shows a worsening trend — escalate treatment urgency.
            </div>
          )}
          {history_trend === "improving" && (
            <div style={{ color: "var(--primary-green)", fontSize: "0.88rem", fontWeight: 600, marginTop: "0.35rem" }}>
              ✅ Your scan history shows an improving trend — continue current treatment.
            </div>
          )}
        </div>
      )}

      {/* Immediate Actions */}
      {immediate_actions.length > 0 && (
        <Section
          icon={<Zap size={16} color="#f97316" />}
          title="Immediate Actions"
          accentColor="#f97316"
        >
          {immediate_actions.map((action, i) => (
            <ActionItem key={i} text={action} icon="⚡" color="#f97316" />
          ))}
        </Section>
      )}

      {/* Treatment Options */}
      {!is_healthy && (treatment_options.organic?.length > 0 || treatment_options.chemical?.length > 0) && (
        <div style={{
          background: "var(--bg-card)", borderRadius: 16,
          border: "1px solid var(--border-color)", overflow: "hidden"
        }}>
          <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--border-color)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Droplets size={16} color="var(--primary-green)" />
              <span style={{ color: "var(--text-primary)", fontWeight: 700 }}>Treatment Options</span>
            </div>
            {treatment_options.note && (
              <div style={{ color: "#f59e0b", fontSize: "0.82rem", marginTop: "0.4rem" }}>
                ⚠️ {treatment_options.note}
              </div>
            )}
          </div>
          {/* Tabs */}
          <div style={{ display: "flex", borderBottom: "1px solid var(--border-color)" }}>
            {["organic", "chemical"].map(tab => (
              <button key={tab} onClick={() => setTreatmentTab(tab)} style={{
                flex: 1, padding: "0.7rem", border: "none", cursor: "pointer",
                background: treatmentTab === tab ? "rgba(16,185,129,0.1)" : "transparent",
                color: treatmentTab === tab ? "var(--primary-green)" : "var(--text-secondary)",
                fontWeight: treatmentTab === tab ? 700 : 400,
                fontSize: "0.88rem", borderBottom: treatmentTab === tab ? "2px solid var(--primary-green)" : "2px solid transparent",
                transition: "all 0.2s"
              }}>
                {tab === "organic" ? "🌿 Organic / Biological" : "🧪 Chemical (Conventional)"}
              </button>
            ))}
          </div>
          <div style={{ padding: "1rem 1.25rem" }}>
            {(treatment_options[treatmentTab] || []).map((item, i) => (
              <div key={i} style={{
                padding: "0.6rem 0", borderBottom: i < treatment_options[treatmentTab].length - 1 ? "1px solid rgba(255,255,255,0.05)" : "none",
                color: "var(--text-secondary)", fontSize: "0.88rem"
              }}>
                • {typeof item === "string" ? item : JSON.stringify(item)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Environmental Actions */}
      {environmental_actions.length > 0 && (
        <Section
          icon={<Eye size={16} color="var(--accent-cyan)" />}
          title="Environmental Context & Actions"
          accentColor="var(--accent-cyan)"
        >
          {environmental_actions.slice(0, 3).map((action, i) => (
            <ActionItem key={i} text={action} icon="🌡️" color="var(--accent-cyan)" />
          ))}
        </Section>
      )}

      {/* Prevention (collapsible) */}
      {prevention.length > 0 && (
        <CollapsibleSection
          icon={<Shield size={16} color="var(--primary-green)" />}
          title="Prevention Measures"
          items={prevention}
          isOpen={expandedSections.prevention}
          onToggle={() => toggleSection("prevention")}
          icon2="🛡️"
          color="var(--primary-green)"
        />
      )}

      {/* Monitoring */}
      {monitoring.next_scan_days && (
        <div style={{
          background: "rgba(16,185,129,0.06)", borderRadius: 14,
          border: "1px solid rgba(16,185,129,0.2)", padding: "1rem 1.25rem",
          display: "flex", flexWrap: "wrap", gap: "1rem", alignItems: "flex-start"
        }}>
          <div style={{ flex: 1, minWidth: 180 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <Clock size={15} color="var(--primary-green)" />
              <span style={{ color: "var(--text-primary)", fontWeight: 700, fontSize: "0.9rem" }}>
                Monitoring Plan
              </span>
            </div>
            <div style={{ color: "var(--primary-green)", fontWeight: 700, fontSize: "1.1rem" }}>
              Next scan in {monitoring.next_scan_days} days
            </div>
            {monitoring.escalation_trigger && (
              <div style={{ color: "#f59e0b", fontSize: "0.8rem", marginTop: "0.4rem" }}>
                🔔 {monitoring.escalation_trigger}
              </div>
            )}
          </div>
          {monitoring.watch_for?.length > 0 && (
            <div style={{ flex: 1, minWidth: 180 }}>
              <div style={{ color: "var(--text-secondary)", fontSize: "0.8rem", marginBottom: "0.35rem", fontWeight: 600 }}>
                WATCH FOR:
              </div>
              {monitoring.watch_for.slice(0, 3).map((item, i) => (
                <div key={i} style={{ color: "var(--text-secondary)", fontSize: "0.83rem", marginBottom: "0.2rem" }}>
                  • {item}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Safety (collapsible) */}
      {safety_information.length > 0 && (
        <CollapsibleSection
          icon={<AlertTriangle size={16} color="#f59e0b" />}
          title="Safety Information"
          items={safety_information}
          isOpen={expandedSections.safety}
          onToggle={() => toggleSection("safety")}
          icon2="⚠️"
          color="#f59e0b"
        />
      )}

      {/* Disclaimer */}
      {disclaimer && (
        <div style={{
          color: "var(--text-secondary)", fontSize: "0.75rem",
          padding: "0.75rem 1rem",
          background: "rgba(255,255,255,0.02)", borderRadius: 10,
          border: "1px solid rgba(255,255,255,0.06)",
          lineHeight: 1.5
        }}>
          <Info size={12} style={{ marginRight: "0.35rem", verticalAlign: "middle" }} />
          {disclaimer}
        </div>
      )}
    </div>
  );
}

function Section({ icon, title, accentColor, children }) {
  return (
    <div style={{
      background: "var(--bg-card)", borderRadius: 16,
      border: "1px solid var(--border-color)", overflow: "hidden"
    }}>
      <div style={{
        padding: "0.9rem 1.25rem", borderBottom: "1px solid var(--border-color)",
        display: "flex", alignItems: "center", gap: "0.5rem"
      }}>
        {icon}
        <span style={{ color: "var(--text-primary)", fontWeight: 700, fontSize: "0.95rem" }}>{title}</span>
      </div>
      <div style={{ padding: "1rem 1.25rem", display: "grid", gap: "0.5rem" }}>
        {children}
      </div>
    </div>
  );
}

function CollapsibleSection({ icon, title, items, isOpen, onToggle, icon2, color }) {
  return (
    <div style={{
      background: "var(--bg-card)", borderRadius: 16,
      border: "1px solid var(--border-color)", overflow: "hidden"
    }}>
      <button onClick={onToggle} style={{
        width: "100%", padding: "0.9rem 1.25rem",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "none", border: "none", cursor: "pointer",
        borderBottom: isOpen ? "1px solid var(--border-color)" : "none"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {icon}
          <span style={{ color: "var(--text-primary)", fontWeight: 700, fontSize: "0.95rem" }}>{title}</span>
          <span style={{ color: "var(--text-secondary)", fontSize: "0.8rem" }}>({items.length})</span>
        </div>
        {isOpen ? <ChevronUp size={16} color="var(--text-secondary)" /> : <ChevronDown size={16} color="var(--text-secondary)" />}
      </button>
      {isOpen && (
        <div style={{ padding: "1rem 1.25rem", display: "grid", gap: "0.5rem" }}>
          {items.map((item, i) => (
            <ActionItem key={i} text={item} icon={icon2} color={color} />
          ))}
        </div>
      )}
    </div>
  );
}

function ActionItem({ text, icon, color }) {
  return (
    <div style={{ display: "flex", gap: "0.6rem", alignItems: "flex-start" }}>
      <span style={{ flexShrink: 0, marginTop: "0.05rem" }}>{icon}</span>
      <span style={{ color: "var(--text-secondary)", fontSize: "0.88rem", lineHeight: 1.5 }}>{text}</span>
    </div>
  );
}
