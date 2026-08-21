package com.greenscan.app.ui

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.model.Recommendations

class RecommendationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val rec = intent.getSerializableExtra("RECOMMENDATION_DATA") as? Recommendations

        val scrollView = ScrollView(this)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        val title = TextView(this).apply {
            text = "📖 Agronomic Recommendation Guide"
            textSize = 24f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 24)
        }
        layout.addView(title)

        if (rec != null) {
            val diseaseHeader = TextView(this).apply {
                text = "${rec.displayName} (${rec.scientificName})"
                textSize = 18f
                setTypeface(null, android.graphics.Typeface.BOLD)
                setTextColor(android.graphics.Color.parseColor("#2E7D32"))
                setPadding(0, 0, 0, 24)
            }
            layout.addView(diseaseHeader)

            layout.addView(createSectionCard("🔍 Symptoms", rec.symptoms))
            layout.addView(createSectionCard("🌱 Root Causes", rec.causes))
            layout.addView(createSectionCard("🌿 Organic Treatment", rec.organicTreatment))
            layout.addView(createSectionCard("🧪 Chemical Treatment", rec.chemicalTreatment))
            layout.addView(createSectionCard("🛡️ Preventive Measures", rec.preventiveMeasures))
            layout.addView(createSectionCard("🌾 Suitable Fertilizer", rec.suitableFertilizer))
            layout.addView(createSectionCard("⏳ Expected Recovery Time", rec.recoveryTime))
        } else {
            val emptyTxt = TextView(this).apply {
                text = "Select a disease from the scan results or disease library to view full treatment guidelines."
                textSize = 16f
                setPadding(0, 24, 0, 0)
            }
            layout.addView(emptyTxt)
        }

        scrollView.addView(layout)
        setContentView(scrollView)
    }

    private fun createSectionCard(headerText: String, bodyText: String): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
            setBackgroundColor(android.graphics.Color.WHITE)
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 8, 0, 16) }
            layoutParams = params

            val head = TextView(context).apply {
                text = headerText
                textSize = 16f
                setTypeface(null, android.graphics.Typeface.BOLD)
                setTextColor(android.graphics.Color.parseColor("#1B5E20"))
            }

            val body = TextView(context).apply {
                text = bodyText
                textSize = 14f
                setTextColor(android.graphics.Color.parseColor("#333333"))
                setPadding(0, 8, 0, 0)
            }

            addView(head)
            addView(body)
        }
    }
}
