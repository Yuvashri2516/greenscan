package com.greenscan.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.model.PredictionResponse
import com.greenscan.app.ui.components.CircularHealthGaugeView

class DashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prediction = intent.getSerializableExtra("PREDICTION_DATA") as? PredictionResponse
        if (prediction == null) {
            Toast.makeText(this, "Failed to load dashboard data", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        val scrollView = ScrollView(this)
        val mainLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        // Header Title
        val titleView = TextView(this).apply {
            text = "📊 Farmer Statistical Dashboard"
            textSize = 24f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
        }
        mainLayout.addView(titleView)

        // 1. Disease Card & Traffic Light Indicator
        val diseaseCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
            setBackgroundColor(android.graphics.Color.WHITE)
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 24, 0, 24) }
            layoutParams = params
        }

        val diseaseText = TextView(this).apply {
            text = "${prediction.gsaMetrics.trafficLight} ${prediction.displayName}"
            textSize = 22f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#2E7D32"))
        }

        val confidenceText = TextView(this).apply {
            text = "Confidence: ${prediction.confidence}% | Severity: ${prediction.gsaMetrics.severityLevel}"
            textSize = 14f
            setTextColor(android.graphics.Color.GRAY)
            setPadding(0, 8, 0, 0)
        }

        diseaseCard.addView(diseaseText)
        diseaseCard.addView(confidenceText)
        mainLayout.addView(diseaseCard)

        // 2. Circular Health Gauge
        val gaugeView = CircularHealthGaugeView(this).apply {
            val params = LinearLayout.LayoutParams(500, 500).apply {
                gravity = android.view.Gravity.CENTER_HORIZONTAL
                setMargins(0, 24, 0, 24)
            }
            layoutParams = params
            setScore(prediction.gsaMetrics.plantHealthScore)
        }
        mainLayout.addView(gaugeView)

        // 3. Quantitative Statistical Metrics (GSA output)
        val statsCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
            setBackgroundColor(android.graphics.Color.WHITE)
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 16, 0, 24) }
            layoutParams = params
        }

        val statsTitle = TextView(this).apply {
            text = "GreenScan Severity Metrics (GSA)"
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setPadding(0, 0, 0, 16)
        }
        statsCard.addView(statsTitle)

        val m1 = createStatRow("Leaf Area", "${prediction.gsaMetrics.leafPixels} pixels")
        val m2 = createStatRow("Activated Pixels", "${prediction.gsaMetrics.activatedPixels} pixels")
        val m3 = createStatRow("Affected Region", "${prediction.gsaMetrics.affectedAreaPct}%")
        val m4 = createStatRow("Weighted Activation", "${prediction.gsaMetrics.weightedActivationScore}")
        val m5 = createStatRow("Risk Level", prediction.gsaMetrics.riskLevel)
        
        statsCard.addView(m1)
        statsCard.addView(m2)
        statsCard.addView(m3)
        statsCard.addView(m4)
        statsCard.addView(m5)
        mainLayout.addView(statsCard)

        // 4. Treatment Priority & Recommendation Summary
        val recCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
            setBackgroundColor(android.graphics.Color.parseColor("#E8F5E9"))
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, 0, 32) }
            layoutParams = params
        }

        val recTitle = TextView(this).apply {
            text = "⚠️ Treatment Priority & Action"
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
        }

        val recBody = TextView(this).apply {
            text = prediction.gsaMetrics.treatmentPriority
            textSize = 14f
            setPadding(0, 8, 0, 16)
        }

        val btnFullRec = Button(this).apply {
            text = "📖 View Full Agronomic Treatment Guide"
            setOnClickListener {
                val intent = Intent(this@DashboardActivity, RecommendationActivity::class.java).apply {
                    putExtra("RECOMMENDATION_DATA", prediction.recommendations)
                }
                startActivity(intent)
            }
        }

        recCard.addView(recTitle)
        recCard.addView(recBody)
        recCard.addView(btnFullRec)
        mainLayout.addView(recCard)

        // 5. Action Buttons (AI Chatbot, Share Report, Download Report)
        val btnChat = Button(this).apply {
            text = "🤖 Ask AI Chatbot About This Diagnosis"
            setBackgroundColor(android.graphics.Color.parseColor("#7B1FA2"))
            setTextColor(android.graphics.Color.WHITE)
            setOnClickListener {
                val intent = Intent(this@DashboardActivity, ChatbotActivity::class.java).apply {
                    putExtra("DISEASE_NAME", prediction.displayName)
                    putExtra("HEALTH_SCORE", prediction.gsaMetrics.plantHealthScore)
                    putExtra("SEVERITY", prediction.gsaMetrics.severityLevel)
                }
                startActivity(intent)
            }
        }

        val btnShare = Button(this).apply {
            text = "📤 Share Report"
            setBackgroundColor(android.graphics.Color.parseColor("#1976D2"))
            setTextColor(android.graphics.Color.WHITE)
            setOnClickListener {
                val shareIntent = Intent().apply {
                    action = Intent.ACTION_SEND
                    putExtra(Intent.EXTRA_TEXT, "GreenScan Analysis Report\nDisease: ${prediction.displayName}\nPlant Health Score: ${prediction.gsaMetrics.plantHealthScore}/100\nSeverity: ${prediction.gsaMetrics.severityLevel}\nTreatment: ${prediction.gsaMetrics.treatmentPriority}")
                    type = "text/plain"
                }
                startActivity(Intent.createChooser(shareIntent, "Share GreenScan Report"))
            }
        }

        mainLayout.addView(btnChat)
        mainLayout.addView(btnShare)

        scrollView.addView(mainLayout)
        setContentView(scrollView)
    }

    private fun createStatRow(label: String, value: String): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 8, 0, 8)
        }
        val lbl = TextView(this).apply {
            text = label
            textSize = 14f
            setTextColor(android.graphics.Color.GRAY)
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val valTxt = TextView(this).apply {
            text = value
            textSize = 14f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.BLACK)
        }
        row.addView(lbl)
        row.addView(valTxt)
        return row
    }
}
