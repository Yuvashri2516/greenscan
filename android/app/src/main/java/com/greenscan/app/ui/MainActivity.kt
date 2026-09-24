package com.greenscan.app.ui

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.Gravity
import android.view.ViewGroup
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {

    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val imageUri: Uri? = result.data?.data
            imageUri?.let { uri ->
                val tempFile = uriToFile(uri)
                if (tempFile != null) {
                    startActivity(
                        Intent(this, ScanningActivity::class.java).apply {
                            putExtra("IMAGE_PATH", tempFile.absolutePath)
                        }
                    )
                } else {
                    Toast.makeText(this, "Unable to load image. Please try another.", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val scrollView = ScrollView(this)
        scrollView.isFillViewport = true

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        root.addView(buildHeroSection())
        root.addView(buildActionSection())
        root.addView(buildFeatureCardsSection())
        root.addView(buildFooter())

        scrollView.addView(root)
        setContentView(scrollView)

        // Animate main content in
        root.alpha = 0f
        root.animate().alpha(1f).setDuration(600).setStartDelay(100).start()
    }

    // ── Hero Section ─────────────────────────────────────────────────────────
    private fun buildHeroSection(): LinearLayout {
        val hero = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(48, 72, 48, 56)
            setBackgroundColor(Color.parseColor("#1B5E20"))
        }

        val leaf = TextView(this).apply {
            text = "🌿"
            textSize = 56f
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 16 }
            layoutParams = p
        }

        val title = TextView(this).apply {
            text = "GreenScan"
            textSize = 36f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            letterSpacing = 0.04f
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
        }

        val tagline = TextView(this).apply {
            text = "AI-Powered Plant Health & Disease Detection"
            textSize = 15f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            setPadding(0, 12, 0, 0)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
        }

        val subInfo = TextView(this).apply {
            text = "EfficientNet-B0 · Grad-CAM · GSA Assessment"
            textSize = 12f
            setTextColor(Color.parseColor("#66BB6A"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 0)
        }

        hero.addView(leaf)
        hero.addView(title)
        hero.addView(tagline)
        hero.addView(subInfo)
        return hero
    }

    // ── Primary Action Buttons ────────────────────────────────────────────────
    private fun buildActionSection(): LinearLayout {
        val section = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 40, 32, 16)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val sectionLabel = TextView(this).apply {
            text = "GET STARTED"
            textSize = 11f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.12f
            setPadding(0, 0, 0, 16)
        }
        section.addView(sectionLabel)

        // Primary: Scan Leaf
        val btnScan = buildPrimaryButton("📷  Scan a Leaf", Color.parseColor("#2E7D32")) {
            startActivity(Intent(this, CameraActivity::class.java))
        }
        section.addView(btnScan)

        // Secondary: Upload from Gallery
        val btnGallery = buildSecondaryButton("🖼️  Upload from Gallery") {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            galleryLauncher.launch(intent)
        }
        section.addView(btnGallery)

        return section
    }

    // ── Quick Access Row ──────────────────────────────────────────────────────
    private fun buildFeatureCardsSection(): LinearLayout {
        val section = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 16, 32, 8)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val sectionLabel = TextView(this).apply {
            text = "FEATURES"
            textSize = 11f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.12f
            setPadding(0, 16, 0, 16)
        }
        section.addView(sectionLabel)

        // 2x2 grid of feature cards
        val row1 = buildFeatureRow(
            "🔬" to "AI Disease\nDetection",
            "💡" to "Explainable\nAI (Grad-CAM)"
        )
        val row2 = buildFeatureRow(
            "❤️" to "Plant Health\nScore",
            "💊" to "Treatment\nRecommendations"
        )
        section.addView(row1)
        section.addView(row2)

        // Quick-access buttons row
        val divider = buildDivider()
        section.addView(divider)

        val quickLabel = TextView(this).apply {
            text = "QUICK ACCESS"
            textSize = 11f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.12f
            setPadding(0, 20, 0, 12)
        }
        section.addView(quickLabel)

        val quickRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
        }

        val btnHistory = buildQuickButton("📜", "History") {
            startActivity(Intent(this, HistoryActivity::class.java))
        }
        val btnChat = buildQuickButton("🤖", "AI Chat") {
            startActivity(Intent(this, ChatbotActivity::class.java))
        }
        val btnLibrary = buildQuickButton("📚", "Disease\nLibrary") {
            startActivity(Intent(this, RecommendationActivity::class.java))
        }
        val btnAbout = buildQuickButton("ℹ️", "About") {
            startActivity(Intent(this, AboutActivity::class.java))
        }

        quickRow.addView(btnHistory)
        quickRow.addView(btnChat)
        quickRow.addView(btnLibrary)
        quickRow.addView(btnAbout)

        section.addView(quickRow)
        return section
    }

    // ── Footer ────────────────────────────────────────────────────────────────
    private fun buildFooter(): LinearLayout {
        val footer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 24, 32, 48)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }
        val txt = TextView(this).apply {
            text = "Tomato Disease Detection · Healthy · Early Blight · Late Blight"
            textSize = 11f
            setTextColor(Color.parseColor("#9E9E9E"))
            gravity = Gravity.CENTER
        }
        footer.addView(txt)
        return footer
    }

    // ── Builder Helpers ───────────────────────────────────────────────────────
    private fun buildPrimaryButton(label: String, bgColor: Int, onClick: () -> Unit): Button {
        return Button(this).apply {
            text = label
            textSize = 16f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            setBackgroundColor(bgColor)
            setPadding(32, 40, 32, 40)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 16; topMargin = 4 }
            layoutParams = p
            setOnClickListener { onClick() }
            // Pulse animation on creation
            animate().scaleX(1.02f).scaleY(1.02f).setDuration(800)
                .withEndAction { animate().scaleX(1f).scaleY(1f).setDuration(400).start() }
                .start()
        }
    }

    private fun buildSecondaryButton(label: String, onClick: () -> Unit): Button {
        return Button(this).apply {
            text = label
            textSize = 15f
            setTextColor(Color.parseColor("#2E7D32"))
            setBackgroundColor(Color.parseColor("#E8F5E9"))
            setPadding(32, 36, 32, 36)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 8 }
            layoutParams = p
            setOnClickListener { onClick() }
        }
    }

    private fun buildFeatureRow(
        left: Pair<String, String>,
        right: Pair<String, String>
    ): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 16 }
            layoutParams = p
        }

        val bgColors = listOf(
            Color.parseColor("#E8F5E9"),
            Color.parseColor("#E3F2FD")
        )

        listOf(left, right).forEachIndexed { i, (emoji, label) ->
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                gravity = Gravity.CENTER
                setPadding(24, 28, 24, 28)
                setBackgroundColor(bgColors[i])
                val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                    if (i == 0) rightMargin = 8 else leftMargin = 8
                }
                layoutParams = p
            }
            val emojiTxt = TextView(this).apply {
                text = emoji
                textSize = 28f
                gravity = Gravity.CENTER
            }
            val labelTxt = TextView(this).apply {
                text = label
                textSize = 13f
                setTypeface(null, Typeface.BOLD)
                setTextColor(Color.parseColor("#1B5E20"))
                gravity = Gravity.CENTER
                setPadding(0, 8, 0, 0)
            }
            card.addView(emojiTxt)
            card.addView(labelTxt)
            row.addView(card)
        }
        return row
    }

    private fun buildQuickButton(emoji: String, label: String, onClick: () -> Unit): LinearLayout {
        val btn = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(12, 20, 12, 20)
            setBackgroundColor(Color.WHITE)
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                setMargins(4, 0, 4, 0)
            }
            layoutParams = p
            isClickable = true
            isFocusable = true
            setOnClickListener { onClick() }
        }
        val emojiTxt = TextView(this).apply {
            text = emoji
            textSize = 24f
            gravity = Gravity.CENTER
        }
        val labelTxt = TextView(this).apply {
            text = label
            textSize = 11f
            setTextColor(Color.parseColor("#333333"))
            gravity = Gravity.CENTER
            setPadding(0, 6, 0, 0)
        }
        btn.addView(emojiTxt)
        btn.addView(labelTxt)
        return btn
    }

    private fun buildDivider(): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.parseColor("#E0E0E0"))
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1
            ).apply { topMargin = 8 }
            layoutParams = p
        }
    }

    // ── File Helpers ──────────────────────────────────────────────────────────
    private fun uriToFile(uri: Uri): File? {
        return try {
            val inputStream = contentResolver.openInputStream(uri) ?: return null
            val file = File(cacheDir, "upload_leaf_${System.currentTimeMillis()}.jpg")
            FileOutputStream(file).use { out -> inputStream.copyTo(out) }
            inputStream.close()
            file
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
