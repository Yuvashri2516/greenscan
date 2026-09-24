package com.greenscan.app.ui

import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.data.ApiClient

class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scrollView = ScrollView(this)
        val layout = LinearLayout(this).apply {
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
        val hTitle = TextView(this).apply {
            text = "⚙️ Settings"
            textSize = 26f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }
        header.addView(hTitle)
        layout.addView(header)

        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 32, 24, 48)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        // API Config
        val apiCard = buildCard()
        val apiTitle = buildSectionHeader("API Configuration")
        val apiUrl = buildInfoRow("Backend URL", ApiClient.PRODUCTION_URL)
        val apiNote = buildInfoRow("Status", "Production (Render)")
        apiCard.addView(apiTitle)
        apiCard.addView(apiUrl)
        apiCard.addView(apiNote)
        content.addView(apiCard)
        content.addView(buildSpacer())

        // Model Info
        val modelCard = buildCard()
        val modelTitle = buildSectionHeader("AI Model")
        val modelName = buildInfoRow("Architecture", "EfficientNet-B0")
        val modelTask = buildInfoRow("Task", "Tomato Leaf Disease Classification")
        val modelClasses = buildInfoRow("Classes", "Healthy · Early Blight · Late Blight")
        val modelXai = buildInfoRow("Explainability", "Grad-CAM + GSA Assessment")
        modelCard.addView(modelTitle)
        modelCard.addView(modelName)
        modelCard.addView(modelTask)
        modelCard.addView(modelClasses)
        modelCard.addView(modelXai)
        content.addView(modelCard)

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
            textSize = 15f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 16)
        }
    }

    private fun buildInfoRow(label: String, value: String): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 8, 0, 8)
        }
        val lbl = TextView(this).apply {
            text = label
            textSize = 13f
            setTextColor(Color.parseColor("#666666"))
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            layoutParams = p
        }
        val val_ = TextView(this).apply {
            text = value
            textSize = 13f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1A1A1A"))
        }
        row.addView(lbl)
        row.addView(val_)
        return row
    }

    private fun buildSpacer(): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 12)
        }
    }
}
