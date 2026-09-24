import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { User, Save, Edit3, CheckCircle, AlertCircle, MapPin, Droplets, Sprout, Leaf } from "lucide-react";
import { createFarmerProfile, getFarmerProfile, updateFarmerProfile } from "../api/index.js";

const CROP_STAGES = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvest"];
const IRRIGATION_METHODS = ["Drip", "Sprinkler", "Overhead", "Flood", "Rainfed"];
const TOMATO_VARIETIES = [
  "Cherry Tomato", "Roma / Plum", "Beefsteak", "Heirloom",
  "Hybrid (F1)", "Kesar", "Pusa Ruby", "Arka Vikas", "Other"
];

const INITIAL_FORM = {
  name: "", farm_name: "", farm_location: "",
  farm_size: "", contact: "", tomato_variety: "",
  crop_stage: "", irrigation_method: "", pin: ""
};

export default function FarmerProfilePage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_FORM);
  const [existing, setExisting] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [status, setStatus] = useState(null); // { type: "success"|"error", message }

  // Load existing profile from localStorage + backend on mount
  useEffect(() => {
    const storedId = localStorage.getItem("greenscan_farmer_id");
    if (storedId) {
      getFarmerProfile(storedId)
        .then(data => {
          if (data?.farmer) {
            setExisting(data.farmer);
            setForm({ ...INITIAL_FORM, ...data.farmer, pin: "" });
          }
        })
        .catch(() => {
          localStorage.removeItem("greenscan_farmer_id");
        });
    } else {
      setIsEditing(true); // No profile yet — show form immediately
    }
  }, []);

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!form.name.trim()) {
      setStatus({ type: "error", message: "Your name is required to create a profile." });
      return;
    }
    setIsSaving(true);
    setStatus(null);
    try {
      const payload = {
        ...form,
        farm_size: form.farm_size ? parseFloat(form.farm_size) : null,
        crop: "Tomato",
      };
      // Remove empty strings
      Object.keys(payload).forEach(k => {
        if (payload[k] === "" || payload[k] === null) delete payload[k];
      });

      let farmer_id;
      if (existing) {
        // Update existing profile
        await updateFarmerProfile(existing.farmer_id, payload);
        farmer_id = existing.farmer_id;
        setStatus({ type: "success", message: "Profile updated successfully!" });
      } else {
        // Create new profile
        const res = await createFarmerProfile(payload);
        farmer_id = res.farmer_id;
        localStorage.setItem("greenscan_farmer_id", farmer_id);
        setStatus({ type: "success", message: "Profile created! Your Farmer ID has been saved." });
      }
      // Reload profile
      const reloaded = await getFarmerProfile(farmer_id);
      if (reloaded?.farmer) {
        setExisting(reloaded.farmer);
        setForm({ ...INITIAL_FORM, ...reloaded.farmer, pin: "" });
      }
      setIsEditing(false);
    } catch (err) {
      setStatus({ type: "error", message: err.message || "Failed to save profile. Please try again." });
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("greenscan_farmer_id");
    setExisting(null);
    setForm(INITIAL_FORM);
    setIsEditing(true);
    setStatus({ type: "success", message: "Profile cleared from this device." });
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", padding: "2rem 1rem" }}>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: 72, height: 72, borderRadius: "50%",
            background: "linear-gradient(135deg, var(--primary-green), var(--accent-cyan))",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 1rem",
            boxShadow: "0 0 32px rgba(16,185,129,0.35)"
          }}>
            <User size={32} color="white" />
          </div>
          <h1 style={{ color: "var(--text-primary)", fontSize: "1.8rem", fontWeight: 700, margin: 0 }}>
            Farmer Profile
          </h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "0.5rem" }}>
            {existing
              ? "Your profile personalizes GreenScan recommendations for your farm."
              : "Create a profile to get personalized disease recommendations, track scan history, and view crop health trends."}
          </p>
        </div>

        {/* Status Message */}
        {status && (
          <div style={{
            display: "flex", alignItems: "center", gap: "0.75rem",
            padding: "1rem 1.25rem", borderRadius: 12, marginBottom: "1.5rem",
            background: status.type === "success"
              ? "rgba(16,185,129,0.12)" : "rgba(239,68,68,0.12)",
            border: `1px solid ${status.type === "success" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
            color: status.type === "success" ? "var(--primary-green)" : "#ef4444"
          }}>
            {status.type === "success"
              ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
            {status.message}
          </div>
        )}

        {/* Profile Card */}
        <div style={{
          background: "var(--bg-card)", borderRadius: 20,
          border: "1px solid var(--border-color)", overflow: "hidden",
          boxShadow: "0 8px 32px rgba(0,0,0,0.2)"
        }}>
          {/* Card Header */}
          <div style={{
            padding: "1.25rem 1.5rem",
            borderBottom: "1px solid var(--border-color)",
            display: "flex", justifyContent: "space-between", alignItems: "center",
            background: "rgba(16,185,129,0.05)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Leaf size={18} color="var(--primary-green)" />
              <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>
                {existing ? `Farm: ${existing.farm_name || existing.name}` : "New Profile"}
              </span>
            </div>
            {existing && !isEditing && (
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <button
                  onClick={() => setIsEditing(true)}
                  style={{
                    display: "flex", alignItems: "center", gap: "0.4rem",
                    background: "rgba(16,185,129,0.15)", border: "1px solid var(--primary-green)",
                    color: "var(--primary-green)", padding: "0.5rem 1rem",
                    borderRadius: 8, cursor: "pointer", fontSize: "0.85rem", fontWeight: 600
                  }}>
                  <Edit3 size={14} /> Edit
                </button>
                <button
                  onClick={() => navigate("/dashboard")}
                  style={{
                    display: "flex", alignItems: "center", gap: "0.4rem",
                    background: "rgba(6,182,212,0.12)", border: "1px solid var(--accent-cyan)",
                    color: "var(--accent-cyan)", padding: "0.5rem 1rem",
                    borderRadius: 8, cursor: "pointer", fontSize: "0.85rem", fontWeight: 600
                  }}>
                  View Dashboard
                </button>
              </div>
            )}
          </div>

          {/* Form Body */}
          <div style={{ padding: "1.5rem", display: "grid", gap: "1.25rem" }}>

            {/* Name */}
            <FormField
              label="Your Full Name *" icon={<User size={16} />}
              value={form.name} onChange={v => handleChange("name", v)}
              placeholder="e.g., Raju Patel" disabled={!isEditing}
            />

            {/* Farm Name */}
            <FormField
              label="Farm Name" icon={<Sprout size={16} />}
              value={form.farm_name} onChange={v => handleChange("farm_name", v)}
              placeholder="e.g., Green Valley Farm" disabled={!isEditing}
            />

            {/* Location + Farm Size (2-col) */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <FormField
                label="Location" icon={<MapPin size={16} />}
                value={form.farm_location} onChange={v => handleChange("farm_location", v)}
                placeholder="Village / District" disabled={!isEditing}
              />
              <FormField
                label="Farm Size (acres)" icon={<span style={{fontSize:"0.9rem"}}>🌾</span>}
                value={form.farm_size} onChange={v => handleChange("farm_size", v)}
                placeholder="e.g., 2.5" type="number" disabled={!isEditing}
              />
            </div>

            {/* Contact */}
            <FormField
              label="Contact / Phone" icon={<span style={{fontSize:"0.9rem"}}>📞</span>}
              value={form.contact} onChange={v => handleChange("contact", v)}
              placeholder="e.g., 9876543210" disabled={!isEditing}
            />

            {/* Tomato Variety + Crop Stage (2-col) */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <SelectField
                label="Tomato Variety" value={form.tomato_variety}
                onChange={v => handleChange("tomato_variety", v)}
                options={TOMATO_VARIETIES} disabled={!isEditing}
              />
              <SelectField
                label="Crop Stage" value={form.crop_stage}
                onChange={v => handleChange("crop_stage", v)}
                options={CROP_STAGES} disabled={!isEditing}
              />
            </div>

            {/* Irrigation */}
            <SelectField
              label="Irrigation Method" icon={<Droplets size={16} />}
              value={form.irrigation_method}
              onChange={v => handleChange("irrigation_method", v)}
              options={IRRIGATION_METHODS} disabled={!isEditing}
            />

            {/* PIN */}
            {isEditing && (
              <FormField
                label="Security PIN (optional, 4 digits)" icon={<span style={{fontSize:"0.9rem"}}>🔒</span>}
                value={form.pin} onChange={v => handleChange("pin", v)}
                placeholder="Leave blank for no PIN" type="password"
                maxLength={4} disabled={!isEditing}
              />
            )}

          </div>

          {/* Farmer ID display */}
          {existing && (
            <div style={{
              padding: "0.75rem 1.5rem",
              borderTop: "1px solid var(--border-color)",
              fontSize: "0.78rem", color: "var(--text-secondary)",
              fontFamily: "monospace"
            }}>
              Farmer ID: {existing.farmer_id} · Member since: {new Date(existing.created_at).toLocaleDateString()}
            </div>
          )}

          {/* Action Buttons */}
          {isEditing && (
            <div style={{
              padding: "1.25rem 1.5rem",
              borderTop: "1px solid var(--border-color)",
              display: "flex", gap: "1rem"
            }}>
              <button
                id="save-profile-btn"
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  flex: 1, display: "flex", alignItems: "center", justifyContent: "center",
                  gap: "0.5rem", padding: "0.9rem",
                  background: "linear-gradient(135deg, var(--primary-green), var(--accent-cyan))",
                  border: "none", borderRadius: 12, color: "white",
                  fontSize: "1rem", fontWeight: 700, cursor: isSaving ? "not-allowed" : "pointer",
                  opacity: isSaving ? 0.75 : 1,
                  boxShadow: "0 4px 20px rgba(16,185,129,0.4)",
                  transition: "all 0.2s"
                }}>
                <Save size={18} />
                {isSaving ? "Saving..." : existing ? "Update Profile" : "Create Profile"}
              </button>
              {existing && (
                <button
                  onClick={() => { setIsEditing(false); setForm({ ...INITIAL_FORM, ...existing, pin: "" }); }}
                  style={{
                    padding: "0.9rem 1.5rem",
                    background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-color)",
                    borderRadius: 12, color: "var(--text-secondary)",
                    fontSize: "0.9rem", cursor: "pointer"
                  }}>
                  Cancel
                </button>
              )}
            </div>
          )}
        </div>

        {/* Logout button */}
        {existing && (
          <div style={{ textAlign: "center", marginTop: "1.5rem" }}>
            <button
              onClick={handleLogout}
              style={{
                background: "none", border: "1px solid rgba(239,68,68,0.3)",
                color: "rgba(239,68,68,0.7)", padding: "0.5rem 1.5rem",
                borderRadius: 8, cursor: "pointer", fontSize: "0.85rem"
              }}>
              Clear Profile from This Device
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function FormField({ label, value, onChange, placeholder, type = "text", disabled, maxLength, icon }) {
  return (
    <div>
      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "0.4rem", fontWeight: 500 }}>
        {icon} {label}
      </label>
      <input
        type={type}
        value={value || ""}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        style={{
          width: "100%", padding: "0.75rem 1rem",
          background: disabled ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.07)",
          border: `1px solid ${disabled ? "rgba(255,255,255,0.08)" : "var(--border-color)"}`,
          borderRadius: 10, color: "var(--text-primary)", fontSize: "0.95rem",
          outline: "none", boxSizing: "border-box",
          transition: "border-color 0.2s",
          cursor: disabled ? "default" : "text"
        }}
        onFocus={e => !disabled && (e.target.style.borderColor = "var(--primary-green)")}
        onBlur={e => e.target.style.borderColor = "var(--border-color)"}
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options, disabled, icon }) {
  return (
    <div>
      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "0.4rem", fontWeight: 500 }}>
        {icon} {label}
      </label>
      <select
        value={value || ""}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        style={{
          width: "100%", padding: "0.75rem 1rem",
          background: disabled ? "rgba(255,255,255,0.03)" : "var(--bg-secondary)",
          border: `1px solid ${disabled ? "rgba(255,255,255,0.08)" : "var(--border-color)"}`,
          borderRadius: 10, color: value ? "var(--text-primary)" : "var(--text-secondary)",
          fontSize: "0.95rem", outline: "none", cursor: disabled ? "default" : "pointer",
          boxSizing: "border-box"
        }}>
        <option value="">— Select —</option>
        {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
      </select>
    </div>
  );
}
