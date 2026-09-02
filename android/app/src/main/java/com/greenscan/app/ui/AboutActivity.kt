package com.greenscan.app.ui

import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class AboutActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scrollView = ScrollView(this)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        // Hero header
        val header = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(40, 56, 40, 48)
            setBackgroundColor(Color.parseColor("#1B5E20"))
        }
        val leaf = TextView(this).apply {
            text = "🌿"
            textSize = 56f
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 12 }
            layoutParams = p
        }
        val name = TextView(this).apply {
            text = "GreenScan"
            textSize = 32f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            letterSpacing = 0.04f
        }
        val version = TextView(this).apply {
            text = "Version 1.0.0"
            textSize = 14f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 0)
        }
        header.addView(leaf)
        header.addView(name)
        header.addView(version)
        layout.addView(header)

        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 32, 24, 64)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        // Description
        val descCard = buildCard()
        val descTitle = buildSectionHeader("About GreenScan")
        val descBody = buildBodyText(
            "GreenScan is an AI-powered plant disease detection system for tomato leaves. " +
            "It uses EfficientNet-B0 deep learning, Grad-CAM explainability, " +
            "and the GreenScan Assessment (GSA) framework to provide detailed disease analysis, " +
            "health scoring, and treatment recommendations."
        )
        descCard.addView(descTitle)
        descCard.addView(descBody)
        content.addView(descCard)
        content.addView(buildSpacer())

        // Technology stack
        val techCard = buildCard()
        val techTitle = buildSectionHeader("Technology Stack")
        val techItems = listOf(
            "🧠 EfficientNet-B0" to "Disease classification model",
            "🔬 Grad-CAM" to "Explainable AI visualization",
            "📊 GSA Engine" to "GreenScan Severity Assessment",
            "🐍 FastAPI" to "Python backend on Render",
            "📱 Android Kotlin" to "Mobile application",
            "🔗 Retrofit + OkHttp" to "Network layer"
        )
        techCard.addView(techTitle)
        techItems.forEach { (tech, desc) ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                setPadding(0, 8, 0, 8)
            }
            val tech_ = TextView(this).apply {
                text = tech
                textSize = 13f
                setTypeface(null, Typeface.BOLD)
                setTextColor(Color.parseColor("#1B5E20"))
                val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                layoutParams = p
            }
            val desc_ = TextView(this).apply {
                text = desc
                textSize = 13f
                setTextColor(Color.parseColor("#555555"))
            }
            row.addView(tech_)
            row.addView(desc_)
            techCard.addView(row)
        }
        content.addView(techCard)
        content.addView(buildSpacer())

        // Disease support
        val disCard = buildCard()
        val disTitle = buildSectionHeader("Supported Diseases")
        val disBody = buildBodyText(
            "✅ Tomato Healthy\n🟡 Tomato Early Blight (Alternaria solani)\n🔴 Tomato Late Blight (Phytophthora infestans)"
        )
        disCard.addView(disTitle)
        disCard.addView(disBody)
        content.addView(disCard)
        content.addView(buildSpacer())

        // Backend info
        val apiCard = buildCard()
        val apiTitle = buildSectionHeader("Backend API")
        val apiBody = buildBodyText("https://greenscan-bot5.onrender.com\n\nDeployed on Render — free tier with cold start (~30s on first request).")
        apiCard.addView(apiTitle)
        apiCard.addView(apiBody)
        content.addView(apiCard)

        layout.addView(content)
        scrollView.addView(layout)
        setContentView(scrollView)
    }

    private fun buildCard(): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 24)
            setBackgroundColor(Color.WHITE)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
        }
    }

    private fun buildSectionHeader(title: String): TextView {
        return TextView(this).apply {
            text = title
            textSize = 16f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 14)
        }
    }

    private fun buildBodyText(text: String): TextView {
        return TextView(this).apply {
            this.text = text
            textSize = 14f
            setTextColor(Color.parseColor("#333333"))
            setLineSpacing(0f, 1.5f)
        }
    }

    private fun buildSpacer(): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 12)
        }
    }
}
