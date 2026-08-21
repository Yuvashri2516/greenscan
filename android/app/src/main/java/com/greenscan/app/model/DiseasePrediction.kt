package com.greenscan.app.model

import com.google.gson.annotations.SerializedName
import java.io.Serializable

data class PredictionResponse(
    @SerializedName("disease_name") val diseaseName: String,
    @SerializedName("display_name") val displayName: String,
    @SerializedName("confidence") val confidence: Double,
    @SerializedName("is_healthy") val isHealthy: Boolean,
    @SerializedName("quality_info") val qualityInfo: QualityInfo,
    @SerializedName("gsa_metrics") val gsaMetrics: GsaMetrics,
    @SerializedName("recommendations") val recommendations: Recommendations
) : Serializable

data class QualityInfo(
    @SerializedName("passed") val passed: Boolean,
    @SerializedName("laplacian_variance") val laplacianVariance: Double,
    @SerializedName("mean_brightness") val meanBrightness: Double,
    @SerializedName("reasons") val reasons: List<String>
) : Serializable

data class GsaMetrics(
    @SerializedName("leaf_pixels") val leafPixels: Int,
    @SerializedName("activated_pixels") val activatedPixels: Int,
    @SerializedName("affected_area_pct") val affectedAreaPct: Double,
    @SerializedName("weighted_activation_score") val weightedActivationScore: Double,
    @SerializedName("plant_health_score") val plantHealthScore: Int,
    @SerializedName("severity_level") val severityLevel: String,
    @SerializedName("traffic_light") val trafficLight: String,
    @SerializedName("traffic_code") val trafficCode: String,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("treatment_priority") val treatmentPriority: String
) : Serializable

data class Recommendations(
    @SerializedName("disease_key") val diseaseKey: String,
    @SerializedName("display_name") val displayName: String,
    @SerializedName("scientific_name") val scientificName: String,
    @SerializedName("symptoms") val symptoms: String,
    @SerializedName("causes") val causes: String,
    @SerializedName("organic_treatment") val organicTreatment: String,
    @SerializedName("chemical_treatment") val chemicalTreatment: String,
    @SerializedName("preventive_measures") val preventiveMeasures: String,
    @SerializedName("suitable_fertilizer") val suitableFertilizer: String,
    @SerializedName("recovery_time") val recoveryTime: String,
    @SerializedName("severity_context") val severityContext: String
) : Serializable
