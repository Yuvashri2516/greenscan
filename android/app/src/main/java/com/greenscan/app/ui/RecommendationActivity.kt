package com.greenscan.app.ui

import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.model.PredictionResponse

class RecommendationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Receive full PredictionResponse from DashboardActivity
        val prediction = intent.getSerializableExtra("PREDICTION_DATA_REC") as? PredictionResponse

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
        val headerTitle = TextView(this).apply {
            text = "📖 Treatment Guide"
            textSize = 26f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }
        val headerSub = TextView(this).apply {
            text = prediction?.displayName ?: "Disease Library"
            textSize = 15f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 0)
        }
        header.addView(headerTitle)
        header.addView(headerSub)
        layout.addView(header)

        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 24, 24, 48)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        if (prediction == null) {
            // No prediction data — show generic library message
            val emptyCard = buildCard()
            val emptyTxt = TextView(this).apply {
                text = "Select a disease from your scan results to view the full treatment guide here.\n\n" +
                       "Supported diseases:\n• Tomato Healthy\n• Tomato Early Blight\n• Tomato Late Blight"
                textSize = 15f
                setTextColor(Color.parseColor("#555555"))
                setLineSpacing(0f, 1.5f)
            }
            emptyCard.addView(emptyTxt)
            content.addView(emptyCard)
        } else {
            val info = prediction.diseaseInfo
            val rec = prediction.recommendations

            // Safety warning if not reliable
            if (!prediction.isReliable) {
                val warnCard = LinearLayout(this).apply {
                    orientation = LinearLayout.VERTICAL
                    setPadding(24, 20, 24, 20)
                    setBackgroundColor(Color.parseColor("#FFF3E0"))
                    val p = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply { bottomMargin = 16 }
                    layoutParams = p
                }
                val warnTxt = TextView(this).apply {
                    text = "⚠️ ${rec?.safetyWarning ?: "Low confidence result. Please re-scan with a clearer image."}"
                    textSize = 13f
                    setTextColor(Color.parseColor("#E65100"))
                    setLineSpacing(0f, 1.4f)
                }
                warnCard.addView(warnTxt)
                content.addView(warnCard)
            }

            // Disease Overview Card
            if (info != null) {
                val overviewCard = buildCard()
                val diseaseName = TextView(this).apply {
                    text = info.displayName ?: prediction.displayName
                    textSize = 22f
                    setTypeface(null, Typeface.BOLD)
                    setTextColor(Color.parseColor("#1B5E20"))
                    setPadding(0, 0, 0, 4)
                }
                overviewCard.addView(diseaseName)
                info.scientificName?.let { sci ->
                    val sciView = TextView(this).apply {
                        text = "Scientific name: $sci"
                        textSize = 13f
                        setTextColor(Color.parseColor("#666666"))
                        setPadding(0, 0, 0, 8)
                    }
                    overviewCard.addView(sciView)
                }
                info.spreadRate?.let { sr ->
                    val spreadView = TextView(this).apply {
                        text = "Spread Rate: $sr"
                        textSize = 13f
                        setTextColor(Color.parseColor("#777777"))
                    }
                    overviewCard.addView(spreadView)
                }
                content.addView(overviewCard)
                content.addView(buildSpacer())

                // Symptom sections
                info.symptoms?.let { content.addView(buildSection("🔍 Symptoms", it, Color.parseColor("#E8F5E9"))) }
                info.causes?.let { content.addView(buildSection("🌧️ Root Causes", it, Color.parseColor("#FFF8E1"))) }
                info.organicTreatment?.let { content.addView(buildSection("🌿 Organic Treatment", it, Color.parseColor("#E8F5E9"))) }
                info.chemicalTreatment?.let { content.addView(buildSection("🧪 Chemical Treatment", it, Color.parseColor("#E3F2FD"))) }
                info.preventiveMeasures?.let { content.addView(buildSection("🛡️ Preventive Measures", it, Color.parseColor("#F3E5F5"))) }
                info.suitableFertilizer?.let { content.addView(buildSection("🌾 Suitable Fertilizer", it, Color.parseColor("#FFF9C4"))) }
                info.recoveryTime?.let { content.addView(buildSection("⏳ Expected Recovery", it, Color.parseColor("#E0F2F1"))) }
            }

            // Recommendations (from backend recommendations field)
            rec?.let { r ->
                if (!r.organic.isNullOrEmpty() && info?.organicTreatment == null) {
                    content.addView(buildListSection("🌿 Organic Recommendations", r.organic, Color.parseColor("#E8F5E9")))
                }
                if (!r.chemical.isNullOrEmpty() && info?.chemicalTreatment == null) {
                    content.addView(buildListSection("🧪 Chemical Recommendations", r.chemical, Color.parseColor("#E3F2FD")))
                }
                if (!r.preventive.isNullOrEmpty() && info?.preventiveMeasures == null) {
                    content.addView(buildListSection("🛡️ Prevention Tips", r.preventive, Color.parseColor("#F3E5F5")))
                }
            }
        }

        // Back button
        val btnBack = Button(this).apply {
            text = "← Back to Results"
            textSize = 14f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setPadding(24, 32, 24, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { topMargin = 8 }
            layoutParams = p
            setOnClickListener { finish() }
        }
        content.addView(btnBack)

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

    private fun buildSection(title: String, body: String, accentColor: Int): LinearLayout {
        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.WHITE)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
        }
        // Color accent left strip
        val strip = android.view.View(this).apply {
            setBackgroundColor(accentColor)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 6)
        }
        card.addView(strip)

        val inner = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 20, 24, 24)
        }
        val hdr = TextView(this).apply {
            text = title
            textSize = 15f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 10)
        }
        val bdy = TextView(this).apply {
            text = body
            textSize = 14f
            setTextColor(Color.parseColor("#333333"))
            setLineSpacing(0f, 1.5f)
        }
        inner.addView(hdr)
        inner.addView(bdy)
        card.addView(inner)
        return card
    }

    private fun buildListSection(title: String, items: List<String>, accentColor: Int): LinearLayout {
        val body = items.joinToString("\n") { "• $it" }
        return buildSection(title, body, accentColor)
    }

    private fun buildSpacer(): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 12)
        }
    }
}
