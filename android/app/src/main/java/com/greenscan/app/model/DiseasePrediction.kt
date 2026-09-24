package com.greenscan.app.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

// ─── Top-level Prediction Response ───────────────────────────────────────────
data class PredictionResponse(
    @SerializedName("disease_name")       val diseaseName: String,
    @SerializedName("display_name")       val displayName: String,
    @SerializedName("confidence")         val confidence: Double,
    @SerializedName("is_healthy")         val isHealthy: Boolean,
    @SerializedName("is_reliable")        val isReliable: Boolean = true,
    @SerializedName("unreliable_reasons") val unreliableReasons: List<String> = emptyList(),
    @SerializedName("quality_info")       val qualityInfo: QualityInfo?,
    @SerializedName("disease_info")       val diseaseInfo: DiseaseInfo?,
    @SerializedName("progression")        val progression: Progression?,
    @SerializedName("gsa_metrics")        val gsaMetrics: GsaMetrics,
    @SerializedName("research_details")   val researchDetails: ResearchDetails?,
    @SerializedName("recommendations")    val recommendations: Recommendations?
) : Serializable

// ─── Quality Check Info ───────────────────────────────────────────────────────
data class QualityInfo(
    @SerializedName("passed")             val passed: Boolean,
    @SerializedName("laplacian_variance") val laplacianVariance: Double?,
    @SerializedName("mean_brightness")    val meanBrightness: Double?,
    @SerializedName("reasons")            val reasons: List<String>?
) : Serializable

// ─── Disease Information (from disease_db.py) ────────────────────────────────
data class DiseaseInfo(
    @SerializedName("key")                val key: String?,
    @SerializedName("display_name")       val displayName: String?,
    @SerializedName("scientific_name")    val scientificName: String?,
    @SerializedName("symptoms")           val symptoms: String?,
    @SerializedName("causes")             val causes: String?,
    @SerializedName("organic_treatment")  val organicTreatment: String?,
    @SerializedName("chemical_treatment") val chemicalTreatment: String?,
    @SerializedName("preventive_measures")val preventiveMeasures: String?,
    @SerializedName("suitable_fertilizer")val suitableFertilizer: String?,
    @SerializedName("recovery_time")      val recoveryTime: String?,
    @SerializedName("spread_rate")        val spreadRate: String?
) : Serializable

// ─── Disease Progression Forecast ────────────────────────────────────────────
data class Progression(
    @SerializedName("current_stage")      val currentStage: String?,
    @SerializedName("next_stage")         val nextStage: String?,
    @SerializedName("days_to_next_stage") val daysToNextStage: Int?,
    @SerializedName("spread_risk")        val spreadRisk: String?,
    @SerializedName("action_urgency")     val actionUrgency: String?
) : Serializable

// ─── GSA Severity Metrics ─────────────────────────────────────────────────────
data class GsaMetrics(
    @SerializedName("leaf_pixels")        val leafPixels: Int,
    @SerializedName("activated_pixels")   val activatedPixels: Int,
    // Both field names present in backend response for backward-compat
    @SerializedName("affected_area_pct")  val affectedAreaPct: Double,
    @SerializedName("attention_affected_region_percent") val attentionAffectedPct: Double?,
    @SerializedName("weighted_activation_score") val weightedActivationScore: Double?,
    @SerializedName("plant_health_score") val plantHealthScore: Int,
    @SerializedName("severity_level")     val severityLevel: String,
    @SerializedName("traffic_light")      val trafficLight: String,
    @SerializedName("traffic_code")       val trafficCode: String,
    @SerializedName("risk_level")         val riskLevel: String,
    @SerializedName("treatment_priority") val treatmentPriority: String
) : Serializable

// ─── Research Details (Grad-CAM visuals) ─────────────────────────────────────
data class ResearchDetails(
    @SerializedName("leaf_pixels")                       val leafPixels: Int?,
    @SerializedName("activated_pixels")                  val activatedPixels: Int?,
    @SerializedName("attention_affected_region_percent") val attentionAffectedPct: Double?,
    @SerializedName("mean_leaf_activation")              val meanLeafActivation: Double?,
    @SerializedName("mean_activated_activation")         val meanActivatedActivation: Double?,
    @SerializedName("threshold_used")                    val thresholdUsed: Double?,
    @SerializedName("visuals")                           val visuals: Visuals?
) : Serializable

// ─── Grad-CAM Visual Assets (base64 encoded images) ──────────────────────────
data class Visuals(
    @SerializedName("original")          val original: String?,      // data:image/jpeg;base64,...
    @SerializedName("heatmap")           val heatmap: String?,        // Grad-CAM overlay
    @SerializedName("leaf_mask")         val leafMask: String?,       // Binary leaf mask
    @SerializedName("activation_mask")   val activationMask: String?, // Activated region mask
    @SerializedName("overlay")           val overlay: String?         // Red overlay on affected area
) : Serializable

// ─── Recommendations (actual backend structure) ───────────────────────────────
// Backend returns {"organic": [...], "chemical": [...], "preventive": [...], "safety_warning": "..."}
// When is_reliable=false, all organic/chemical are empty and safety_warning is populated.
data class Recommendations(
    @SerializedName("organic")        val organic: List<String>?,
    @SerializedName("chemical")       val chemical: List<String>?,
    @SerializedName("preventive")     val preventive: List<String>?,
    @SerializedName("safety_warning") val safetyWarning: String?
) : Serializable
