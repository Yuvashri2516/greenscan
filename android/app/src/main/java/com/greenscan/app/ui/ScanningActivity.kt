package com.greenscan.app.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.greenscan.app.data.ApiClient
import com.greenscan.app.data.AppDatabase
import com.greenscan.app.data.GreenScanRepository
import kotlinx.coroutines.launch
import java.io.File

class ScanningActivity : AppCompatActivity() {

    private lateinit var analysisStepsLayout: LinearLayout
    private val stepViews = mutableListOf<TextView>()

    // Analysis step labels
    private val steps = listOf(
        "○  Image quality check",
        "○  Leaf segmentation",
        "○  Disease classification (EfficientNet-B0)",
        "○  GreenScan Assessment (GSA)",
        "○  Generating recommendations"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val imagePath = intent.getStringExtra("IMAGE_PATH")
        if (imagePath == null) {
            Toast.makeText(this, "No image file found.", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        val file = File(imagePath)
        if (!file.exists()) {
            Toast.makeText(this, "Image file not found. Please try again.", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Show preview screen first
        setContentView(buildPreviewLayout(file))
    }

    // ── Preview Layout ─────────────────────────────────────────────────────────
    private fun buildPreviewLayout(file: File): ScrollView {
        val scrollView = ScrollView(this)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        // Header
        val header = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(48, 40, 48, 32)
            setBackgroundColor(Color.parseColor("#1B5E20"))
        }
        val headerTitle = TextView(this).apply {
            text = "🌿 Scan Your Leaf"
            textSize = 24f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }
        val headerSub = TextView(this).apply {
            text = "Upload a clear image of a tomato leaf"
            textSize = 14f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 0)
        }
        header.addView(headerTitle)
        header.addView(headerSub)
        layout.addView(header)

        // Image Preview Card
        val cardPad = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 32, 32, 16)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val previewCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.WHITE)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 16 }
            layoutParams = p
        }

        val previewLabel = TextView(this).apply {
            text = "Selected Image"
            textSize = 12f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.1f
            setPadding(24, 20, 24, 8)
        }

        val imageView = ImageView(this).apply {
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 900
            ).apply { setMargins(0, 0, 0, 0) }
            layoutParams = p
            scaleType = ImageView.ScaleType.CENTER_CROP
            try {
                setImageURI(Uri.fromFile(file))
            } catch (e: Exception) {
                setBackgroundColor(Color.parseColor("#E8F5E9"))
            }
        }

        val imageMeta = TextView(this).apply {
            text = "📁 ${file.name}  ·  ${formatFileSize(file.length())}"
            textSize = 12f
            setTextColor(Color.parseColor("#9E9E9E"))
            setPadding(24, 12, 24, 20)
        }

        previewCard.addView(previewLabel)
        previewCard.addView(imageView)
        previewCard.addView(imageMeta)
        cardPad.addView(previewCard)

        // Analyze Button
        val btnAnalyze = Button(this).apply {
            text = "🔬  Analyze Leaf"
            textSize = 17f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setPadding(32, 40, 32, 40)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
            setOnClickListener {
                setContentView(buildAnalyzingLayout())
                startAnalysis(file)
            }
        }

        // Retake / Back Button
        val btnRetake = Button(this).apply {
            text = "↩  Choose Different Image"
            textSize = 15f
            setTextColor(Color.parseColor("#555555"))
            setBackgroundColor(Color.parseColor("#EEEEEE"))
            setPadding(32, 32, 32, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
            setOnClickListener { finish() }
        }

        cardPad.addView(btnAnalyze)
        cardPad.addView(btnRetake)
        layout.addView(cardPad)
        scrollView.addView(layout)
        return scrollView
    }

    // ── Analysis Loading Layout ────────────────────────────────────────────────
    private fun buildAnalyzingLayout(): LinearLayout {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
        }

        // Top accent bar
        val accentBar = android.view.View(this).apply {
            setBackgroundColor(Color.parseColor("#1B5E20"))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 8
            )
        }
        root.addView(accentBar)

        val contentArea = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(48, 72, 48, 48)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
        }

        val leafEmoji = TextView(this).apply {
            text = "🌿"
            textSize = 56f
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 24 }
            layoutParams = p
        }

        // Pulse animation on leaf emoji
        leafEmoji.animate()
            .scaleX(1.1f).scaleY(1.1f).setDuration(700)
            .withEndAction {
                leafEmoji.animate().scaleX(1f).scaleY(1f).setDuration(700)
                    .withEndAction {
                        leafEmoji.animate().scaleX(1.1f).scaleY(1.1f).setDuration(700).start()
                    }.start()
            }.start()

        val title = TextView(this).apply {
            text = "Analyzing your leaf…"
            textSize = 24f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1B5E20"))
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 8 }
            layoutParams = p
        }

        val subtitle = TextView(this).apply {
            text = "This may take 30–60 seconds\nif the server is starting up"
            textSize = 13f
            setTextColor(Color.parseColor("#888888"))
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 40 }
            layoutParams = p
        }

        val progressBar = ProgressBar(this).apply {
            isIndeterminate = true
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 48 }
            layoutParams = p
        }

        // Steps card
        val stepsCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 28, 32, 28)
            setBackgroundColor(Color.WHITE)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
        }

        val stepsTitle = TextView(this).apply {
            text = "ANALYSIS PIPELINE"
            textSize = 11f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.1f
            setPadding(0, 0, 0, 16)
        }
        stepsCard.addView(stepsTitle)

        analysisStepsLayout = stepsCard
        stepViews.clear()
        steps.forEach { step ->
            val stepTxt = TextView(this).apply {
                text = step
                textSize = 14f
                setTextColor(Color.parseColor("#9E9E9E"))
                setPadding(0, 8, 0, 8)
            }
            stepViews.add(stepTxt)
            stepsCard.addView(stepTxt)
        }

        contentArea.addView(leafEmoji)
        contentArea.addView(title)
        contentArea.addView(subtitle)
        contentArea.addView(progressBar)
        contentArea.addView(stepsCard)
        root.addView(contentArea)

        // Start animating steps
        animateSteps()
        return root
    }

    // Progressively tick steps with visual feedback
    private fun animateSteps() {
        val handler = Handler(Looper.getMainLooper())
        val delays = listOf(800L, 2000L, 4000L, 7000L, 10000L)
        steps.forEachIndexed { i, label ->
            handler.postDelayed({
                if (i < stepViews.size) {
                    // Mark previous as done
                    if (i > 0) {
                        stepViews[i - 1].text = "✓  ${steps[i - 1].drop(3)}"
                        stepViews[i - 1].setTextColor(Color.parseColor("#2E7D32"))
                    }
                    // Mark current as in-progress
                    stepViews[i].text = "⟳  ${label.drop(3)}"
                    stepViews[i].setTextColor(Color.parseColor("#1976D2"))
                    stepViews[i].setTypeface(null, Typeface.BOLD)
                }
            }, delays[i])
        }
    }

    // ── API Call ───────────────────────────────────────────────────────────────
    private fun startAnalysis(file: File) {
        lifecycleScope.launch {
            val db = AppDatabase.getDatabase(applicationContext)
            val repository = GreenScanRepository(ApiClient.apiService, db.historyDao())
            val result = repository.predictLeafDisease(file)

            result.onSuccess { response ->
                // Mark all steps complete
                stepViews.forEachIndexed { i, tv ->
                    tv.text = "✓  ${steps[i].drop(3)}"
                    tv.setTextColor(Color.parseColor("#2E7D32"))
                    tv.setTypeface(null, Typeface.NORMAL)
                }
                // Navigate to Dashboard
                Handler(Looper.getMainLooper()).postDelayed({
                    val intent = Intent(this@ScanningActivity, DashboardActivity::class.java).apply {
                        putExtra("PREDICTION_DATA", response)
                    }
                    startActivity(intent)
                    finish()
                }, 500)

            }.onFailure { err ->
                setContentView(buildErrorLayout(err.message ?: "Unknown error"))
            }
        }
    }

    // ── Error Layout ───────────────────────────────────────────────────────────
    private fun buildErrorLayout(message: String): LinearLayout {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(48, 64, 48, 64)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val emoji = TextView(this).apply {
            text = "⚠️"
            textSize = 56f
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 24 }
            layoutParams = p
        }

        val title = TextView(this).apply {
            text = "Analysis Failed"
            textSize = 24f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#C62828"))
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 16 }
            layoutParams = p
        }

        val msgBox = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 24, 28, 24)
            setBackgroundColor(Color.parseColor("#FFF3E0"))
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 32 }
            layoutParams = p
        }
        val msgTxt = TextView(this).apply {
            text = message
            textSize = 14f
            setTextColor(Color.parseColor("#E65100"))
            gravity = Gravity.CENTER
        }
        msgBox.addView(msgTxt)

        val btnRetry = Button(this).apply {
            text = "↺  Retry Analysis"
            textSize = 15f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setPadding(32, 36, 32, 36)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
            setOnClickListener { finish() }
        }

        val btnChoose = Button(this).apply {
            text = "📷  Choose Another Image"
            textSize = 14f
            setTextColor(Color.parseColor("#1976D2"))
            setBackgroundColor(Color.parseColor("#E3F2FD"))
            setPadding(32, 32, 32, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
            setOnClickListener { finish() }
        }

        root.addView(emoji)
        root.addView(title)
        root.addView(msgBox)
        root.addView(btnRetry)
        root.addView(btnChoose)
        return root
    }

    private fun formatFileSize(bytes: Long): String {
        return if (bytes < 1024) "$bytes B"
        else if (bytes < 1024 * 1024) "${bytes / 1024} KB"
        else "${bytes / (1024 * 1024)} MB"
    }
}
