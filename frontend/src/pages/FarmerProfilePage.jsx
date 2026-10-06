import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  User, Save, Edit3, CheckCircle, AlertCircle, MapPin, 
  Droplets, Sprout, Leaf, Phone, Activity 
} from "lucide-react";
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
    <div style={{ minHeight: "100vh", background: "var(--green-50)", padding: "2.5rem 1.5rem" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>

        {/* Page Header */}
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ color: "var(--gray-900)", fontSize: "1.85rem", fontWeight: 800, margin: 0, letterSpacing: "-0.02em" }}>
            Farmer Profile
          </h1>
          <p style={{ color: "var(--gray-600)", marginTop: "0.4rem", fontSize: "0.95rem" }}>
            {existing
              ? "Manage your agricultural profile, farm details, and crop configuration."
              : "Create a profile to get personalized disease recommendations, track scan history, and view crop health trends."}
          </p>
        </div>

        {/* Status Message */}
        {status && (
          <div style={{
            display: "flex", alignItems: "center", gap: "0.75rem",
            padding: "1rem 1.25rem", borderRadius: 12, marginBottom: "1.5rem",
            background: status.type === "success" ? "var(--green-100)" : "#fef2f2",
            border: `1.5px solid ${status.type === "success" ? "var(--green-200)" : "#fecaca"}`,
            color: status.type === "success" ? "var(--green-800)" : "var(--accent-red)",
            fontWeight: 600, fontSize: "0.9rem"
          }}>
            {status.type === "success"
              ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
            {status.message}
          </div>
        )}

        {/* Profile Summary Header Banner */}
        <div style={{
          background: "var(--white)", borderRadius: 16,
          border: "1.5px solid var(--gray-200)", padding: "1.25rem 1.5rem",
          marginBottom: "1.5rem", boxShadow: "var(--shadow-card)",
          display: "flex", justifyContent: "space-between", alignItems: "center",
          flexWrap: "wrap", gap: "1rem"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <div style={{
              width: 52, height: 52, borderRadius: "50%",
              background: "var(--green-100)", border: "1.5px solid var(--green-200)",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <Leaf size={24} color="var(--green-700)" />
            </div>
            <div>
              <h2 style={{ color: "var(--gray-900)", fontSize: "1.35rem", fontWeight: 800, margin: 0 }}>
                {existing ? (existing.farm_name || existing.name) : "New Profile"}
              </h2>
              {existing && (
                <p style={{ color: "var(--gray-600)", margin: "0.2rem 0 0", fontSize: "0.88rem", fontWeight: 500 }}>
                  {existing.name} {existing.farm_location ? `· ${existing.farm_location}` : ""}
                </p>
              )}
            </div>
          </div>

          {existing && !isEditing && (
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                onClick={() => setIsEditing(true)}
                style={{
                  display: "inline-flex", alignItems: "center", gap: "0.4rem",
                  background: "var(--green-100)", border: "1.5px solid var(--green-200)",
                  color: "var(--green-800)", padding: "0.6rem 1.2rem",
                  borderRadius: 10, cursor: "pointer", fontSize: "0.88rem", fontWeight: 700,
                  transition: "all 0.2s"
                }}
                onMouseEnter={e => e.currentTarget.style.background = "var(--green-200)"}
                onMouseLeave={e => e.currentTarget.style.background = "var(--green-100)"}
              >
                <Edit3 size={15} /> Edit Profile
              </button>
              <button
                onClick={() => navigate("/dashboard")}
                style={{
                  display: "inline-flex", alignItems: "center", gap: "0.4rem",
                  background: "#eff6ff", border: "1.5px solid #bfdbfe",
                  color: "var(--accent-blue)", padding: "0.6rem 1.2rem",
                  borderRadius: 10, cursor: "pointer", fontSize: "0.88rem", fontWeight: 700,
                  transition: "all 0.2s"
                }}
                onMouseEnter={e => e.currentTarget.style.background = "#dbeafe"}
                onMouseLeave={e => e.currentTarget.style.background = "#eff6ff"}
              >
                View Dashboard
              </button>
            </div>
          )}
        </div>

        {/* View Mode Section Cards Grid */}
        {!isEditing && existing && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem", marginBottom: "1.5rem" }}>
            
            {/* Section A: Farmer Information */}
            <div style={{ background: "var(--white)", borderRadius: 16, border: "1.5px solid var(--gray-200)", padding: "1.5rem", boxShadow: "var(--shadow-card)" }}>
              <h3 style={{ margin: "0 0 1.25rem", color: "var(--gray-900)", fontSize: "1.1rem", fontWeight: 800, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <User size={18} color="var(--green-700)" /> Farmer Information
              </h3>
              <div style={{ display: "grid", gap: "1rem" }}>
                <InfoField label="FULL NAME" value={existing.name} icon={<User size={14} />} />
                <InfoField label="CONTACT / PHONE" value={existing.contact} icon={<Phone size={14} />} />
              </div>
            </div>

            {/* Section B: Farm Information */}
            <div style={{ background: "var(--white)", borderRadius: 16, border: "1.5px solid var(--gray-200)", padding: "1.5rem", boxShadow: "var(--shadow-card)" }}>
              <h3 style={{ margin: "0 0 1.25rem", color: "var(--gray-900)", fontSize: "1.1rem", fontWeight: 800, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Sprout size={18} color="var(--green-700)" /> Farm Information
              </h3>
              <div style={{ display: "grid", gap: "1rem" }}>
                <InfoField label="FARM NAME" value={existing.farm_name} icon={<Sprout size={14} />} />
                <InfoField label="LOCATION" value={existing.farm_location} icon={<MapPin size={14} />} />
                <InfoField label="FARM SIZE" value={existing.farm_size ? `${existing.farm_size} acres` : null} icon={<span style={{fontSize:"0.85rem"}}>🌾</span>} />
              </div>
            </div>

            {/* Section C: Crop Configuration */}
            <div style={{ background: "var(--white)", borderRadius: 16, border: "1.5px solid var(--gray-200)", padding: "1.5rem", boxShadow: "var(--shadow-card)" }}>
              <h3 style={{ margin: "0 0 1.25rem", color: "var(--gray-900)", fontSize: "1.1rem", fontWeight: 800, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Leaf size={18} color="var(--green-700)" /> Crop Configuration
              </h3>
              <div style={{ display: "grid", gap: "1rem" }}>
                <InfoField label="TOMATO VARIETY" value={existing.tomato_variety} icon={<Leaf size={14} />} />
                <InfoField label="CROP STAGE" value={existing.crop_stage} icon={<Activity size={14} />} />
                <InfoField label="IRRIGATION METHOD" value={existing.irrigation_method} icon={<Droplets size={14} />} />
              </div>
            </div>

          </div>
        )}

        {/* Edit / New Profile Form Card */}
        {isEditing && (
          <div style={{
            background: "var(--white)", borderRadius: 16,
            border: "1.5px solid var(--gray-200)", overflow: "hidden",
            boxShadow: "var(--shadow-card)", marginBottom: "1.5rem"
          }}>
            <div style={{
              padding: "1.25rem 1.5rem",
              borderBottom: "1.5px solid var(--gray-200)",
              background: "var(--green-50)",
              display: "flex", alignItems: "center", gap: "0.6rem"
            }}>
              <Leaf size={18} color="var(--green-700)" />
              <span style={{ color: "var(--gray-900)", fontWeight: 800, fontSize: "1.05rem" }}>
                {existing ? "Edit Farmer Profile" : "Create Farmer Profile"}
              </span>
            </div>

            {/* Form Fields Body */}
            <div style={{ padding: "1.75rem 1.5rem", display: "grid", gap: "1.5rem" }}>

              {/* Section 1: Farmer Information */}
              <div>
                <h4 style={{ margin: "0 0 1rem", color: "var(--green-800)", fontSize: "0.95rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  1. Farmer Information
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.25rem" }}>
                  <FormField
                    label="Your Full Name *" icon={<User size={16} />}
                    value={form.name} onChange={v => handleChange("name", v)}
                    placeholder="e.g., Raju Patel" disabled={false}
                  />
                  <FormField
                    label="Contact / Phone" icon={<Phone size={16} />}
                    value={form.contact} onChange={v => handleChange("contact", v)}
                    placeholder="e.g., 9876543210" disabled={false}
                  />
                </div>
              </div>

              {/* Section 2: Farm Details */}
              <div>
                <h4 style={{ margin: "0 0 1rem", color: "var(--green-800)", fontSize: "0.95rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  2. Farm Details
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
                  <FormField
                    label="Farm Name" icon={<Sprout size={16} />}
                    value={form.farm_name} onChange={v => handleChange("farm_name", v)}
                    placeholder="e.g., Green Valley Farm" disabled={false}
                  />
                  <FormField
                    label="Location" icon={<MapPin size={16} />}
                    value={form.farm_location} onChange={v => handleChange("farm_location", v)}
                    placeholder="Village / District" disabled={false}
                  />
                  <FormField
                    label="Farm Size (acres)" icon={<span style={{fontSize:"0.9rem"}}>🌾</span>}
                    value={form.farm_size} onChange={v => handleChange("farm_size", v)}
                    placeholder="e.g., 2.5" type="number" disabled={false}
                  />
                </div>
              </div>

              {/* Section 3: Crop Configuration */}
              <div>
                <h4 style={{ margin: "0 0 1rem", color: "var(--green-800)", fontSize: "0.95rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                  3. Crop Configuration
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.25rem" }}>
                  <SelectField
                    label="Tomato Variety" value={form.tomato_variety}
                    onChange={v => handleChange("tomato_variety", v)}
                    options={TOMATO_VARIETIES} disabled={false}
                  />
                  <SelectField
                    label="Crop Stage" value={form.crop_stage}
                    onChange={v => handleChange("crop_stage", v)}
                    options={CROP_STAGES} disabled={false}
                  />
                  <SelectField
                    label="Irrigation Method" icon={<Droplets size={16} />}
                    value={form.irrigation_method}
                    onChange={v => handleChange("irrigation_method", v)}
                    options={IRRIGATION_METHODS} disabled={false}
                  />
                </div>
              </div>

              {/* PIN Option */}
              <FormField
                label="Security PIN (optional, 4 digits)" icon={<span style={{fontSize:"0.9rem"}}>🔒</span>}
                value={form.pin} onChange={v => handleChange("pin", v)}
                placeholder="Leave blank for no PIN" type="password"
                maxLength={4} disabled={false}
              />

            </div>

            {/* Action Buttons */}
            <div style={{
              padding: "1.25rem 1.5rem",
              borderTop: "1.5px solid var(--gray-200)",
              background: "var(--gray-50)",
              display: "flex", gap: "1rem"
            }}>
              <button
                id="save-profile-btn"
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  flex: 1, display: "inline-flex", alignItems: "center", justifyContent: "center",
                  gap: "0.5rem", padding: "0.85rem 1.5rem",
                  background: "var(--green-700)",
                  border: "none", borderRadius: 10, color: "white",
                  fontSize: "0.95rem", fontWeight: 700, cursor: isSaving ? "not-allowed" : "pointer",
                  opacity: isSaving ? 0.75 : 1,
                  boxShadow: "0 4px 14px rgba(27,143,58,0.35)",
                  transition: "all 0.2s"
                }}
                onMouseEnter={e => e.currentTarget.style.background = "var(--green-800)"}
                onMouseLeave={e => e.currentTarget.style.background = "var(--green-700)"}
              >
                <Save size={18} />
                {isSaving ? "Saving..." : existing ? "Update Profile" : "Create Profile"}
              </button>
              {existing && (
                <button
                  onClick={() => { setIsEditing(false); setForm({ ...INITIAL_FORM, ...existing, pin: "" }); }}
                  style={{
                    padding: "0.85rem 1.5rem",
                    background: "var(--white)", border: "1.5px solid var(--gray-200)",
                    borderRadius: 10, color: "var(--gray-700)", fontWeight: 600,
                    fontSize: "0.9rem", cursor: "pointer"
                  }}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        )}

        {/* Farmer ID Display & Logout */}
        {existing && (
          <div style={{ 
            background: "var(--white)", borderRadius: 16, border: "1.5px solid var(--gray-200)", 
            padding: "1rem 1.5rem", display: "flex", justifyContent: "space-between", 
            alignItems: "center", flexWrap: "wrap", gap: "1rem" 
          }}>
            <div style={{ fontSize: "0.82rem", color: "var(--gray-600)", fontFamily: "monospace" }}>
              Farmer ID: <strong>{existing.farmer_id}</strong> · Member since: {new Date(existing.created_at).toLocaleDateString()}
            </div>
            <button
              onClick={handleLogout}
              style={{
                background: "none", border: "1.5px solid #fecaca",
                color: "var(--accent-red)", padding: "0.45rem 1.1rem",
                borderRadius: 8, cursor: "pointer", fontSize: "0.82rem", fontWeight: 600
              }}>
              Clear Profile from This Device
            </button>
          </div>
        )}

      </div>
    </div>
  );
}

function InfoField({ label, value, icon }) {
  return (
    <div style={{ background: "var(--gray-50)", padding: "1rem 1.15rem", borderRadius: 12, border: "1.5px solid var(--gray-200)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--gray-600)", fontSize: "0.78rem", fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: "0.35rem" }}>
        {icon && <span style={{ color: "var(--green-700)" }}>{icon}</span>}
        <span>{label}</span>
      </div>
      <div style={{ color: "var(--gray-900)", fontSize: "1.1rem", fontWeight: 700 }}>
        {value || "—"}
      </div>
    </div>
  );
}

function FormField({ label, value, onChange, placeholder, type = "text", disabled, maxLength, icon }) {
  const isRequired = label.includes('*');
  const cleanLabel = label.replace('*', '').trim();
  return (
    <div>
      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--gray-800)", fontSize: "0.88rem", marginBottom: "0.45rem", fontWeight: 600 }}>
        {icon && <span style={{ color: "var(--green-700)" }}>{icon}</span>}
        <span>{cleanLabel}</span>
        {isRequired && <span style={{ color: "var(--accent-red)", fontWeight: 700 }}>*</span>}
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
          background: disabled ? "var(--gray-50)" : "var(--white)",
          border: "1.5px solid var(--gray-200)",
          borderRadius: 10, color: "var(--gray-900)", fontSize: "0.95rem",
          outline: "none", boxSizing: "border-box",
          transition: "border-color 0.2s, box-shadow 0.2s",
          cursor: disabled ? "not-allowed" : "text"
        }}
        onFocus={e => !disabled && (e.target.style.borderColor = "var(--green-700)", e.target.style.boxShadow = "0 0 0 3px rgba(27,143,58,0.15)")}
        onBlur={e => (e.target.style.borderColor = "var(--gray-200)", e.target.style.boxShadow = "none")}
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options, disabled, icon }) {
  return (
    <div>
      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "var(--gray-800)", fontSize: "0.88rem", marginBottom: "0.45rem", fontWeight: 600 }}>
        {icon && <span style={{ color: "var(--green-700)" }}>{icon}</span>}
        <span>{label}</span>
      </label>
      <select
        value={value || ""}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        style={{
          width: "100%", padding: "0.75rem 1rem",
          background: disabled ? "var(--gray-50)" : "var(--white)",
          border: "1.5px solid var(--gray-200)",
          borderRadius: 10, color: value ? "var(--gray-900)" : "var(--gray-600)",
          fontSize: "0.95rem", outline: "none", cursor: disabled ? "not-allowed" : "pointer",
          boxSizing: "border-box"
        }}
        onFocus={e => !disabled && (e.target.style.borderColor = "var(--green-700)", e.target.style.boxShadow = "0 0 0 3px rgba(27,143,58,0.15)")}
        onBlur={e => (e.target.style.borderColor = "var(--gray-200)", e.target.style.boxShadow = "none")}
      >
        <option value="">— Select —</option>
        {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
      </select>
    </div>
  );
}
