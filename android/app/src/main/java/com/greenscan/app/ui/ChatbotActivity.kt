package com.greenscan.app.ui

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.greenscan.app.data.ApiClient
import com.greenscan.app.data.AppDatabase
import com.greenscan.app.data.GreenScanRepository
import com.greenscan.app.model.ChatMessage
import kotlinx.coroutines.launch

class ChatbotActivity : AppCompatActivity() {

    private val messagesList = mutableListOf<ChatMessage>()
    private lateinit var chatContainer: LinearLayout
    private lateinit var scrollView: ScrollView
    private lateinit var inputEditText: EditText
    private lateinit var repository: GreenScanRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val db = AppDatabase.getDatabase(applicationContext)
        repository = GreenScanRepository(ApiClient.apiService, db.historyDao())

        val diseaseName = intent.getStringExtra("DISEASE_NAME") ?: "Tomato Plant"
        val healthScore = intent.getIntExtra("HEALTH_SCORE", 100)
        val severity = intent.getStringExtra("SEVERITY") ?: "Normal"

        val mainLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        // Header Title
        val header = TextView(this).apply {
            text = "🤖 GreenScan AI Assistant"
            textSize = 20f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.WHITE)
            setBackgroundColor(android.graphics.Color.parseColor("#1B5E20"))
            setPadding(32, 32, 32, 32)
        }
        mainLayout.addView(header)

        // Context Banner
        val contextBanner = TextView(this).apply {
            text = "Active Scan: $diseaseName | Health Score: $healthScore/100 | Severity: $severity"
            textSize = 12f
            setTextColor(android.graphics.Color.parseColor("#2E7D32"))
            setBackgroundColor(android.graphics.Color.parseColor("#E8F5E9"))
            setPadding(24, 16, 24, 16)
        }
        mainLayout.addView(contextBanner)

        // Scrollable Chat Area
        scrollView = ScrollView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f
            )
        }

        chatContainer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 24)
        }
        scrollView.addView(chatContainer)
        mainLayout.addView(scrollView)

        // Input Controls
        val inputRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(16, 16, 16, 16)
            setBackgroundColor(android.graphics.Color.WHITE)
        }

        inputEditText = EditText(this).apply {
            hint = "Ask organic treatment, fungicide dosage, fertilizer..."
            textSize = 14f
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }

        val sendBtn = Button(this).apply {
            text = "Send"
            setBackgroundColor(android.graphics.Color.parseColor("#2E7D32"))
            setTextColor(android.graphics.Color.WHITE)
            setOnClickListener {
                val text = inputEditText.text.toString().trim()
                if (text.isNotEmpty()) {
                    addMessage(text, isUser = true)
                    inputEditText.text.clear()
                    sendToBot(text, diseaseName, healthScore, severity)
                }
            }
        }

        inputRow.addView(inputEditText)
        inputRow.addView(sendBtn)
        mainLayout.addView(inputRow)

        setContentView(mainLayout)

        // Initial Greeting
        addMessage("Hello! I am GreenScan AI. Ask me anything about $diseaseName, organic/chemical sprays, fertilizer, or prevention!", isUser = false)
    }

    private fun addMessage(text: String, isUser: Boolean) {
        val bubble = TextView(this).apply {
            this.text = text
            textSize = 14f
            setPadding(24, 16, 24, 16)
            setTextColor(if (isUser) android.graphics.Color.WHITE else android.graphics.Color.BLACK)
            setBackgroundColor(
                if (isUser) android.graphics.Color.parseColor("#2E7D32")
                else android.graphics.Color.WHITE
            )
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                gravity = if (isUser) android.view.Gravity.END else android.view.Gravity.START
                setMargins(0, 8, 0, 8)
            }
            layoutParams = params
        }
        chatContainer.addView(bubble)
        scrollView.post { scrollView.fullScroll(ScrollView.FOCUS_DOWN) }
    }

    private fun sendToBot(userText: String, disease: String, phs: Int, severity: String) {
        lifecycleScope.launch {
            val contextMap = mapOf(
                "display_name" to disease,
                "plant_health_score" to phs,
                "severity_level" to severity
            )
            val result = repository.sendChatMessage(userText, contextMap)
            result.onSuccess { res ->
                addMessage(res.reply, isUser = false)
            }.onFailure {
                addMessage("I am having trouble connecting right now. Please try again shortly.", isUser = false)
            }
        }
    }
}
