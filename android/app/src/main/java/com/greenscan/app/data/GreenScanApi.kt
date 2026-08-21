package com.greenscan.app.data

import com.greenscan.app.model.ChatApiRequest
import com.greenscan.app.model.ChatApiResponse
import com.greenscan.app.model.PredictionResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface GreenScanApi {

    @Multipart
    @POST("predict")
    suspend fun predictLeafDisease(
        @Part file: MultipartBody.Part
    ): Response<PredictionResponse>

    @POST("chat")
    suspend fun sendChatMessage(
        @Body request: ChatApiRequest
    ): Response<ChatApiResponse>

    @GET("history")
    suspend fun getScanHistory(
        @Query("limit") limit: Int = 20
    ): Response<Map<String, Any>>

    @GET("tips")
    suspend fun getTips(
        @Query("count") count: Int = 3
    ): Response<Map<String, Any>>
}
