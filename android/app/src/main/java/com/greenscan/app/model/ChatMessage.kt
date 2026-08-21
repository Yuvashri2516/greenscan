package com.greenscan.app.model

import com.google.gson.annotations.SerializedName

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

data class ChatApiRequest(
    @SerializedName("message") val message: String,
    @SerializedName("language") val language: String = "en",
    @SerializedName("context") val context: Map<String, Any>? = null
)

data class ChatApiResponse(
    @SerializedName("reply") val reply: String,
    @SerializedName("disease_context") val diseaseContext: String?,
    @SerializedName("plant_health_score") val plantHealthScore: Int?,
    @SerializedName("severity") val severity: String?
)
