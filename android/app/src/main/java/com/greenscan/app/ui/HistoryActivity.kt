package com.greenscan.app.ui

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
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
            setPadding(48, 48, 48, 48)
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        val title = TextView(this).apply {
            text = "📜 Scan History Log"
            textSize = 24f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 24)
        }
        mainLayout.addView(title)

        val db = AppDatabase.getDatabase(applicationContext)
        val repo = GreenScanRepository(ApiClient.apiService, db.historyDao())

        lifecycleScope.launch {
            repo.allLocalScans.collectLatest { historyList ->
                mainLayout.removeAllViews()
                mainLayout.addView(title)

                if (historyList.isEmpty()) {
                    val emptyView = TextView(this@HistoryActivity).apply {
                        text = "No previous leaf scans recorded yet."
                        textSize = 16f
                        setTextColor(android.graphics.Color.GRAY)
                        setPadding(0, 32, 0, 0)
                    }
                    mainLayout.addView(emptyView)
                } else {
                    for (item in historyList) {
                        val card = LinearLayout(this@HistoryActivity).apply {
                            orientation = LinearLayout.VERTICAL
                            setPadding(24, 24, 24, 24)
                            setBackgroundColor(android.graphics.Color.WHITE)
                            val params = LinearLayout.LayoutParams(
                                LinearLayout.LayoutParams.MATCH_PARENT,
                                LinearLayout.LayoutParams.WRAP_CONTENT
                            ).apply { setMargins(0, 8, 0, 16) }
                            layoutParams = params

                            val t1 = TextView(context).apply {
                                text = "${item.trafficLight} ${item.displayName}"
                                textSize = 16f
                                setTypeface(null, android.graphics.Typeface.BOLD)
                                setTextColor(android.graphics.Color.parseColor("#1B5E20"))
                            }

                            val t2 = TextView(context).apply {
                                text = "Health Score: ${item.plantHealthScore}/100 | Severity: ${item.severityLevel}\nAffected Area: ${item.affectedAreaPct}% | Date: ${item.timestamp}"
                                textSize = 13f
                                setTextColor(android.graphics.Color.GRAY)
                                setPadding(0, 8, 0, 0)
                            }

                            addView(t1)
                            addView(t2)
                        }
                        mainLayout.addView(card)
                    }
                }
            }
        }

        scrollView.addView(mainLayout)
        setContentView(scrollView)
    }
}
