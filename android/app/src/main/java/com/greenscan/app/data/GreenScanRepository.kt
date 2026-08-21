package com.greenscan.app.data

import com.greenscan.app.model.ChatApiRequest
import com.greenscan.app.model.ChatApiResponse
import com.greenscan.app.model.HistoryEntity
import com.greenscan.app.model.PredictionResponse
import kotlinx.coroutines.flow.Flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class GreenScanRepository(
    private val api: GreenScanApi,
    private val historyDao: HistoryDao
) {
    val allLocalScans: Flow<List<HistoryEntity>> = historyDao.getAllScans()

    suspend fun predictLeafDisease(imageFile: File): Result<PredictionResponse> {
        return try {
            val requestFile = imageFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
            val body = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)
            val response = api.predictLeafDisease(body)

            if (response.isSuccessful && response.body() != null) {
                val pred = response.body()!!
                // Cache into Room database
                val historyEntity = HistoryEntity(
                    timestamp = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.getDefault()).format(java.util.Date()),
                    diseaseName = pred.diseaseName,
                    displayName = pred.displayName,
                    confidence = pred.confidence,
                    plantHealthScore = pred.gsaMetrics.plantHealthScore,
                    affectedAreaPct = pred.gsaMetrics.affectedAreaPct,
                    weightedActivation = pred.gsaMetrics.weightedActivationScore,
                    severityLevel = pred.gsaMetrics.severityLevel,
                    riskLevel = pred.gsaMetrics.riskLevel,
                    treatmentPriority = pred.gsaMetrics.treatmentPriority,
                    trafficLight = pred.gsaMetrics.trafficLight,
                    leafPixels = pred.gsaMetrics.leafPixels,
                    activatedPixels = pred.gsaMetrics.activatedPixels
                )
                historyDao.insertScan(historyEntity)
                Result.success(pred)
            } else {
                Result.failure(Exception("API Error: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sendChatMessage(message: String, contextMap: Map<String, Any>? = null): Result<ChatApiResponse> {
        return try {
            val req = ChatApiRequest(message = message, context = contextMap)
            val response = api.sendChatMessage(req)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Chat API failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
