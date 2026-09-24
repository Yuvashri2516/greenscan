package com.greenscan.app.data

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {

    /**
     * Production GreenScan API — deployed on Render.
     * Never use 127.0.0.1 or localhost for production Android builds.
     * For local emulator testing only: use "http://10.0.2.2:8000/"
     */
    const val PRODUCTION_URL = "https://greenscan-bot5.onrender.com/"
    private const val BASE_URL = PRODUCTION_URL

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)   // Render cold-start can take 30–60 s
        .readTimeout(120, TimeUnit.SECONDS)      // EfficientNet inference may take time
        .writeTimeout(60, TimeUnit.SECONDS)
        .addInterceptor(loggingInterceptor)
        .build()

    val apiService: GreenScanApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(GreenScanApi::class.java)
    }
}
