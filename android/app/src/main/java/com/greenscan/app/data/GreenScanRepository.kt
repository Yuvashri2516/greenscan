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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

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

                // Cache to local Room database
                val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date())
                val historyEntity = HistoryEntity(
                    timestamp = timestamp,
                    diseaseName = pred.diseaseName,
                    displayName = pred.displayName,
                    confidence = pred.confidence,
                    plantHealthScore = pred.gsaMetrics.plantHealthScore,
                    affectedAreaPct = pred.gsaMetrics.affectedAreaPct,
                    weightedActivation = pred.gsaMetrics.weightedActivationScore ?: 0.0,
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
                val errorMsg = when (response.code()) {
                    400 -> "Invalid image. Please upload a clear tomato leaf photo."
                    500 -> "Server error during analysis. Please try again."
                    503 -> "GreenScan server is temporarily unavailable."
                    else -> "API Error: ${response.code()} ${response.message()}"
                }
                Result.failure(Exception(errorMsg))
            }
        } catch (e: java.net.SocketTimeoutException) {
            Result.failure(Exception("Request timed out. The server may be warming up — please retry in a moment."))
        } catch (e: java.net.UnknownHostException) {
            Result.failure(Exception("No internet connection. Please check your network."))
        } catch (e: Exception) {
            Result.failure(Exception("Analysis failed: ${e.message}"))
        }
    }

    suspend fun sendChatMessage(
        message: String,
        contextMap: Map<String, Any>? = null
    ): Result<ChatApiResponse> {
        return try {
            val req = ChatApiRequest(message = message, context = contextMap)
            val response = api.sendChatMessage(req)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Chat API failed: ${response.code()}"))
            }
        } catch (e: java.net.UnknownHostException) {
            Result.failure(Exception("No internet connection."))
        } catch (e: Exception) {
            Result.failure(Exception("Chat error: ${e.message}"))
        }
    }
}
