package com.greenscan.app.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "scan_history")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val timestamp: String,
    val diseaseName: String,
    val displayName: String,
    val confidence: Double,
    val plantHealthScore: Int,
    val affectedAreaPct: Double,
    val weightedActivation: Double,
    val severityLevel: String,
    val riskLevel: String,
    val treatmentPriority: String,
    val trafficLight: String,
    val leafPixels: Int,
    val activatedPixels: Int
)
