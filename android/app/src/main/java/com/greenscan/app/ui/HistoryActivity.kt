package com.greenscan.app.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.greenscan.app.data.ApiClient
import com.greenscan.app.data.AppDatabase
import com.greenscan.app.data.GreenScanRepository
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class HistoryActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scrollView = ScrollView(this)
        val mainLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        // Header
        val header = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(40, 48, 40, 36)
            setBackgroundColor(Color.parseColor("#1B5E20"))
        }
        val headerTitle = TextView(this).apply {
            text = "📜 Scan History"
            textSize = 26f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }
        val headerSub = TextView(this).apply {
            text = "Your previous leaf scan results"
            textSize = 14f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 0)
        }
        header.addView(headerTitle)
        header.addView(headerSub)
        mainLayout.addView(header)

        // Content area
        val contentLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 48)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }
        mainLayout.addView(contentLayout)

        // Load history from Room DB
        val db = AppDatabase.getDatabase(applicationContext)
        val repo = GreenScanRepository(ApiClient.apiService, db.historyDao())

        lifecycleScope.launch {
            repo.allLocalScans.collectLatest { historyList ->
                contentLayout.removeAllViews()

                if (historyList.isEmpty()) {
                    val emptyLayout = LinearLayout(this@HistoryActivity).apply {
                        orientation = LinearLayout.VERTICAL
                        gravity = Gravity.CENTER
                        setPadding(40, 80, 40, 80)
                    }
                    val emptyEmoji = TextView(this@HistoryActivity).apply {
                        text = "🌿"
                        textSize = 48f
                        gravity = Gravity.CENTER
                        val p = LinearLayout.LayoutParams(
                            LinearLayout.LayoutParams.WRAP_CONTENT,
                            LinearLayout.LayoutParams.WRAP_CONTENT
                        ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 16 }
                        layoutParams = p
                    }
                    val emptyTitle = TextView(this@HistoryActivity).apply {
                        text = "No scans yet"
                        textSize = 20f
                        setTypeface(null, Typeface.BOLD)
                        setTextColor(Color.parseColor("#555555"))
                        gravity = Gravity.CENTER
                    }
                    val emptyMsg = TextView(this@HistoryActivity).apply {
                        text = "Scan your first leaf to get started.\nYour results will appear here."
                        textSize = 14f
                        setTextColor(Color.parseColor("#888888"))
                        gravity = Gravity.CENTER
                        setPadding(0, 12, 0, 32)
                    }
                    val btnScan = Button(this@HistoryActivity).apply {
                        text = "📷 Scan a Leaf"
                        textSize = 15f
                        setTypeface(null, Typeface.BOLD)
                        setTextColor(Color.WHITE)
                        setBackgroundColor(Color.parseColor("#2E7D32"))
                        setPadding(32, 32, 32, 32)
                        setOnClickListener {
                            startActivity(Intent(this@HistoryActivity, CameraActivity::class.java))
                        }
                    }
                    emptyLayout.addView(emptyEmoji)
                    emptyLayout.addView(emptyTitle)
                    emptyLayout.addView(emptyMsg)
                    emptyLayout.addView(btnScan)
                    contentLayout.addView(emptyLayout)
                } else {
                    // Stats bar
                    val statsBar = LinearLayout(this@HistoryActivity).apply {
                        orientation = LinearLayout.HORIZONTAL
                        setPadding(20, 16, 20, 16)
                        setBackgroundColor(Color.parseColor("#E8F5E9"))
                        val p = LinearLayout.LayoutParams(
                            LinearLayout.LayoutParams.MATCH_PARENT,
                            LinearLayout.LayoutParams.WRAP_CONTENT
                        ).apply { bottomMargin = 16 }
                        layoutParams = p
                    }
                    val totalScans = TextView(this@HistoryActivity).apply {
                        text = "📊 ${historyList.size} total scans"
                        textSize = 13f
                        setTypeface(null, Typeface.BOLD)
                        setTextColor(Color.parseColor("#1B5E20"))
                        val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                        layoutParams = p
                    }
                    val avgHealth = historyList.map { it.plantHealthScore }.average()
                    val avgHealthTxt = TextView(this@HistoryActivity).apply {
                        text = "Avg health: ${String.format("%.0f", avgHealth)}/100"
                        textSize = 13f
                        setTextColor(Color.parseColor("#2E7D32"))
                        gravity = Gravity.END
                    }
                    statsBar.addView(totalScans)
                    statsBar.addView(avgHealthTxt)
                    contentLayout.addView(statsBar)

                    // History entries
                    historyList.forEachIndexed { index, item ->
                        val severityColor = when (item.severityLevel.lowercase()) {
                            "healthy"  -> Color.parseColor("#2E7D32")
                            "mild"     -> Color.parseColor("#FBC02D")
                            "moderate" -> Color.parseColor("#FF9800")
                            "severe"   -> Color.parseColor("#F44336")
                            "critical" -> Color.parseColor("#B71C1C")
                            else       -> Color.parseColor("#666666")
                        }

                        val card = LinearLayout(this@HistoryActivity).apply {
                            orientation = LinearLayout.VERTICAL
                            setBackgroundColor(Color.WHITE)
                            val p = LinearLayout.LayoutParams(
                                LinearLayout.LayoutParams.MATCH_PARENT,
                                LinearLayout.LayoutParams.WRAP_CONTENT
                            ).apply { bottomMargin = 12 }
                            layoutParams = p
                        }

                        // Colored severity strip
                        val strip = android.view.View(this@HistoryActivity).apply {
                            setBackgroundColor(severityColor)
                            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 6)
                        }
                        card.addView(strip)

                        val cardContent = LinearLayout(this@HistoryActivity).apply {
                            orientation = LinearLayout.VERTICAL
                            setPadding(24, 20, 24, 20)
                        }

                        // Row 1: Traffic light + disease name
                        val nameRow = LinearLayout(this@HistoryActivity).apply {
                            orientation = LinearLayout.HORIZONTAL
                            gravity = Gravity.CENTER_VERTICAL
                        }
                        val trafficTxt = TextView(this@HistoryActivity).apply {
                            text = item.trafficLight
                            textSize = 20f
                            val p = LinearLayout.LayoutParams(
                                LinearLayout.LayoutParams.WRAP_CONTENT,
                                LinearLayout.LayoutParams.WRAP_CONTENT
                            ).apply { rightMargin = 10 }
                            layoutParams = p
                        }
                        val nameTxt = TextView(this@HistoryActivity).apply {
                            text = item.displayName
                            textSize = 16f
                            setTypeface(null, Typeface.BOLD)
                            setTextColor(Color.parseColor("#1A1A1A"))
                        }
                        nameRow.addView(trafficTxt)
                        nameRow.addView(nameTxt)

                        // Row 2: Metrics
                        val metricsTxt = TextView(this@HistoryActivity).apply {
                            text = "Health: ${item.plantHealthScore}/100  ·  Severity: ${item.severityLevel}  ·  Confidence: ${item.confidence}%"
                            textSize = 12f
                            setTextColor(Color.parseColor("#666666"))
                            setPadding(0, 8, 0, 4)
                        }

                        // Row 3: Affected area + date
                        val detailsTxt = TextView(this@HistoryActivity).apply {
                            text = "Affected: ${item.affectedAreaPct}%  ·  ${item.timestamp}"
                            textSize = 11f
                            setTextColor(Color.parseColor("#9E9E9E"))
                        }

                        cardContent.addView(nameRow)
                        cardContent.addView(metricsTxt)
                        cardContent.addView(detailsTxt)
                        card.addView(cardContent)
                        contentLayout.addView(card)
                    }
                }
            }
        }

        scrollView.addView(mainLayout)
        setContentView(scrollView)
    }
}
