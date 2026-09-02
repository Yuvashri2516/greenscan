package com.greenscan.app.ui

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.util.Base64
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.model.PredictionResponse
import com.greenscan.app.ui.components.CircularHealthGaugeView

class DashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prediction = intent.getSerializableExtra("PREDICTION_DATA") as? PredictionResponse
        if (prediction == null) {
            Toast.makeText(this, "Failed to load result data.", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        val scrollView = ScrollView(this)
        val mainLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        mainLayout.addView(buildResultHeader(prediction))
        mainLayout.addView(buildHealthGaugeCard(prediction))
        mainLayout.addView(buildGsaMetricsCard(prediction))
        mainLayout.addView(buildGradCamSection(prediction))
        mainLayout.addView(buildDiseaseInfoCard(prediction))
        mainLayout.addView(buildRecommendationsCard(prediction))
        mainLayout.addView(buildActionButtons(prediction))
        mainLayout.addView(buildSpacerView(64))

        scrollView.addView(mainLayout)
        setContentView(scrollView)
    }

    // ── Result Header ──────────────────────────────────────────────────────────
    private fun buildResultHeader(pred: PredictionResponse): LinearLayout {
        val bgColor = when (pred.gsaMetrics.trafficCode) {
            "GREEN"  -> Color.parseColor("#1B5E20")
            "YELLOW" -> Color.parseColor("#F57F17")
            "RED"    -> Color.parseColor("#B71C1C")
            else     -> Color.parseColor("#1B5E20")
        }

        val header = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 48, 32, 40)
            setBackgroundColor(bgColor)
        }

        val trafficEmoji = TextView(this).apply {
            text = pred.gsaMetrics.trafficLight
            textSize = 40f
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; bottomMargin = 12 }
            layoutParams = p
        }

        val diseaseName = TextView(this).apply {
            text = pred.displayName
            textSize = 28f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }

        val confidenceRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(0, 12, 0, 0)
        }

        val confLabel = TextView(this).apply {
            text = "Confidence: "
            textSize = 14f
            setTextColor(Color.parseColor("#CCCCCC"))
        }
        val confValue = TextView(this).apply {
            text = "${pred.confidence}%"
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
        }
        confidenceRow.addView(confLabel)
        confidenceRow.addView(confValue)

        // Reliability warning badge
        if (!pred.isReliable) {
            val warningBadge = TextView(this).apply {
                text = "⚠️ LOW CONFIDENCE — Results may be inaccurate"
                textSize = 12f
                setTextColor(Color.parseColor("#FFECB3"))
                setBackgroundColor(Color.parseColor("#33000000"))
                setPadding(16, 8, 16, 8)
                gravity = Gravity.CENTER
                val p = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply { topMargin = 16 }
                layoutParams = p
            }
            header.addView(warningBadge)
        }

        header.addView(trafficEmoji)
        header.addView(diseaseName)
        header.addView(confidenceRow)
        return header
    }

    // ── Health Gauge Card ──────────────────────────────────────────────────────
    private fun buildHealthGaugeCard(pred: PredictionResponse): LinearLayout {
        val card = buildCard()

        val cardTitle = buildSectionTitle("🌡️ Plant Health Score")
        card.addView(cardTitle)

        // CircularHealthGaugeView
        val gaugeView = CircularHealthGaugeView(this).apply {
            val p = LinearLayout.LayoutParams(460, 460).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                topMargin = 16
                bottomMargin = 8
            }
            layoutParams = p
            setScore(pred.gsaMetrics.plantHealthScore)
        }
        card.addView(gaugeView)

        // Severity badge
        val severityColor = getSeverityColor(pred.gsaMetrics.severityLevel)
        val severityBadge = TextView(this).apply {
            text = "  ${pred.gsaMetrics.severityLevel.uppercase()}  "
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            setBackgroundColor(severityColor)
            setPadding(24, 10, 24, 10)
            gravity = Gravity.CENTER
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { gravity = Gravity.CENTER_HORIZONTAL; topMargin = 8 }
            layoutParams = p
        }
        card.addView(severityBadge)

        val padded = wrapInPadding(card)
        return padded
    }

    // ── GSA Metrics Card ───────────────────────────────────────────────────────
    private fun buildGsaMetricsCard(pred: PredictionResponse): LinearLayout {
        val card = buildCard()
        card.addView(buildSectionTitle("📊 GreenScan Assessment (GSA)"))

        val metrics = listOf(
            "Leaf Pixels" to "${pred.gsaMetrics.leafPixels}",
            "Activated Pixels" to "${pred.gsaMetrics.activatedPixels}",
            "Affected Region" to "${pred.gsaMetrics.affectedAreaPct}%",
            "Risk Level" to pred.gsaMetrics.riskLevel,
            "Severity" to pred.gsaMetrics.severityLevel,
            "Treatment Priority" to pred.gsaMetrics.treatmentPriority
        )

        metrics.forEach { (label, value) ->
            card.addView(buildMetricRow(label, value))
            card.addView(buildThinDivider())
        }

        return wrapInPadding(card)
    }

    // ── Grad-CAM Section ───────────────────────────────────────────────────────
    private fun buildGradCamSection(pred: PredictionResponse): LinearLayout {
        val wrapper = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 8, 24, 0)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val visuals = pred.researchDetails?.visuals
        if (visuals == null) {
            // No Grad-CAM available
            return wrapper
        }

        val card = buildCard()
        card.addView(buildSectionTitle("🔍 Explainable AI — Grad-CAM"))

        val explanationText = TextView(this).apply {
            text = "Highlighted regions indicate areas that most influenced the AI's prediction. " +
                    "This is a model explanation tool — not a definitive clinical diagnosis."
            textSize = 13f
            setTextColor(Color.parseColor("#555555"))
            setPadding(0, 8, 0, 20)
        }
        card.addView(explanationText)

        // Show Original + Heatmap side-by-side (or stacked on small screens)
        val imagesRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
        }

        // Original image
        visuals.original?.let { b64 ->
            val imgWrapper = buildImagePanel("Original Leaf", b64, 0)
            imagesRow.addView(imgWrapper)
        }

        // Heatmap
        visuals.heatmap?.let { b64 ->
            val imgWrapper = buildImagePanel("Grad-CAM Heatmap", b64, 8)
            imagesRow.addView(imgWrapper)
        }

        card.addView(imagesRow)

        // Overlay image (full width)
        visuals.overlay?.let { b64 ->
            val label = TextView(this).apply {
                text = "Affected Region Overlay"
                textSize = 12f
                setTypeface(null, Typeface.BOLD)
                setTextColor(Color.parseColor("#2E7D32"))
                letterSpacing = 0.05f
                setPadding(0, 8, 0, 8)
            }
            card.addView(label)

            val overlayBitmap = base64ToBitmap(b64)
            if (overlayBitmap != null) {
                val overlayImg = ImageView(this).apply {
                    setImageBitmap(overlayBitmap)
                    scaleType = ImageView.ScaleType.CENTER_CROP
                    val p = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, 600
                    )
                    layoutParams = p
                }
                card.addView(overlayImg)
            }
        }

        wrapper.addView(card)
        return wrapper
    }

    private fun buildImagePanel(label: String, base64: String, leftMargin: Int): LinearLayout {
        val panel = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                this.leftMargin = leftMargin
            }
            layoutParams = p
        }
        val lbl = TextView(this).apply {
            text = label
            textSize = 11f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            letterSpacing = 0.05f
            setPadding(0, 0, 0, 6)
        }
        panel.addView(lbl)
        val bitmap = base64ToBitmap(base64)
        if (bitmap != null) {
            val imgView = ImageView(this).apply {
                setImageBitmap(bitmap)
                scaleType = ImageView.ScaleType.CENTER_CROP
                val p = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 400
                )
                layoutParams = p
            }
            panel.addView(imgView)
        } else {
            val errView = TextView(this).apply {
                text = "(Image unavailable)"
                textSize = 12f
                setTextColor(Color.GRAY)
                gravity = Gravity.CENTER
                setBackgroundColor(Color.parseColor("#F5F5F5"))
                val p = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 200
                )
                layoutParams = p
            }
            panel.addView(errView)
        }
        return panel
    }

    // ── Disease Information Card ───────────────────────────────────────────────
    private fun buildDiseaseInfoCard(pred: PredictionResponse): LinearLayout {
        val info = pred.diseaseInfo
        val card = buildCard()
        card.addView(buildSectionTitle("🌱 Disease Information"))

        if (info == null) {
            val noInfo = TextView(this).apply {
                text = "Disease information not available."
                textSize = 14f
                setTextColor(Color.GRAY)
            }
            card.addView(noInfo)
            return wrapInPadding(card)
        }

        info.scientificName?.let { sci ->
            val sciName = TextView(this).apply {
                text = "Scientific name: $sci"
                textSize = 13f
                setTextColor(Color.parseColor("#555555"))
                setPadding(0, 0, 0, 16)
            }
            card.addView(sciName)
        }

        info.symptoms?.let { s -> card.addView(buildInfoSection("🔍 Symptoms", s)) }
        info.causes?.let { c -> card.addView(buildInfoSection("🌧️ Causes", c)) }
        info.spreadRate?.let { sr ->
            card.addView(buildInfoSection("📈 Spread Rate", sr))
        }

        return wrapInPadding(card)
    }

    // ── Recommendations Card ────────────────────────────────────────────────────
    private fun buildRecommendationsCard(pred: PredictionResponse): LinearLayout {
        val rec = pred.recommendations
        val card = buildCard()
        card.addView(buildSectionTitle("💊 Treatment & Recommendations"))

        // Safety warning (when reliability is low)
        rec?.safetyWarning?.let { warning ->
            val warningBox = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(20, 16, 20, 16)
                setBackgroundColor(Color.parseColor("#FFF3E0"))
                val p = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply { bottomMargin = 16 }
                layoutParams = p
            }
            val warnTxt = TextView(this).apply {
                text = "⚠️ $warning"
                textSize = 13f
                setTextColor(Color.parseColor("#E65100"))
            }
            warningBox.addView(warnTxt)
            card.addView(warningBox)
        }

        // Disease info organic/chemical treatment
        pred.diseaseInfo?.let { info ->
            info.organicTreatment?.let { ot ->
                card.addView(buildInfoSection("🌿 Organic Treatment", ot))
            }
            info.chemicalTreatment?.let { ct ->
                card.addView(buildInfoSection("🧪 Chemical Treatment", ct))
            }
            info.preventiveMeasures?.let { pm ->
                card.addView(buildInfoSection("🛡️ Preventive Measures", pm))
            }
            info.suitableFertilizer?.let { sf ->
                card.addView(buildInfoSection("🌾 Suitable Fertilizer", sf))
            }
            info.recoveryTime?.let { rt ->
                card.addView(buildInfoSection("⏳ Recovery Time", rt))
            }
        }

        // Fallback: use recommendations lists if disease_info was empty
        if (pred.diseaseInfo?.organicTreatment == null) {
            rec?.organic?.let { list ->
                if (list.isNotEmpty()) {
                    card.addView(buildInfoSection("🌿 Organic Treatment", list.joinToString("\n• ", "• ")))
                }
            }
            rec?.chemical?.let { list ->
                if (list.isNotEmpty()) {
                    card.addView(buildInfoSection("🧪 Chemical Treatment", list.joinToString("\n• ", "• ")))
                }
            }
        }
        rec?.preventive?.let { list ->
            if (list.isNotEmpty() && pred.diseaseInfo?.preventiveMeasures == null) {
                card.addView(buildInfoSection("🛡️ Preventive Measures", list.joinToString("\n• ", "• ")))
            }
        }

        // View Full Treatment Guide button
        val btnFullGuide = Button(this).apply {
            text = "📖 View Full Treatment Guide"
            textSize = 14f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setPadding(24, 32, 24, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { topMargin = 16 }
            layoutParams = p
            setOnClickListener {
                startActivity(
                    Intent(this@DashboardActivity, RecommendationActivity::class.java).apply {
                        putExtra("PREDICTION_DATA_REC", pred)
                    }
                )
            }
        }
        card.addView(btnFullGuide)

        return wrapInPadding(card)
    }

    // ── Action Buttons ─────────────────────────────────────────────────────────
    private fun buildActionButtons(pred: PredictionResponse): LinearLayout {
        val section = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 8, 24, 8)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
        }

        val btnChat = Button(this).apply {
            text = "🤖 Ask AI Chatbot About This Diagnosis"
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#7B1FA2"))
            setPadding(24, 36, 24, 36)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
            setOnClickListener {
                startActivity(
                    Intent(this@DashboardActivity, ChatbotActivity::class.java).apply {
                        putExtra("DISEASE_NAME", pred.displayName)
                        putExtra("HEALTH_SCORE", pred.gsaMetrics.plantHealthScore)
                        putExtra("SEVERITY", pred.gsaMetrics.severityLevel)
                    }
                )
            }
        }

        val btnShare = Button(this).apply {
            text = "📤 Share Report"
            textSize = 14f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#1565C0"))
            setPadding(24, 32, 24, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { bottomMargin = 12 }
            layoutParams = p
            setOnClickListener {
                val shareText = buildShareText(pred)
                startActivity(
                    Intent.createChooser(
                        Intent(Intent.ACTION_SEND).apply {
                            type = "text/plain"
                            putExtra(Intent.EXTRA_TEXT, shareText)
                            putExtra(Intent.EXTRA_SUBJECT, "GreenScan Report — ${pred.displayName}")
                        },
                        "Share GreenScan Report"
                    )
                )
            }
        }

        val btnNewScan = Button(this).apply {
            text = "🌿 Scan Another Leaf"
            textSize = 14f
            setTextColor(Color.parseColor("#2E7D32"))
            setBackgroundColor(Color.parseColor("#E8F5E9"))
            setPadding(24, 32, 24, 32)
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
            setOnClickListener { finish() }
        }

        section.addView(btnChat)
        section.addView(btnShare)
        section.addView(btnNewScan)
        return section
    }

    // ── Utility Builders ───────────────────────────────────────────────────────
    private fun buildCard(): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 28, 28, 28)
            setBackgroundColor(Color.WHITE)
        }
    }

    private fun wrapInPadding(inner: LinearLayout): LinearLayout {
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(24, 12, 24, 0)
            setBackgroundColor(Color.parseColor("#F4F6F8"))
            val p = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            layoutParams = p
            addView(inner)
        }
    }

    private fun buildSectionTitle(text: String): TextView {
        return TextView(this).apply {
            this.text = text
            textSize = 16f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 16)
        }
    }

    private fun buildMetricRow(label: String, value: String): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 10, 0, 10)
        }
        val lbl = TextView(this).apply {
            text = label
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            val p = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            layoutParams = p
        }
        val val_ = TextView(this).apply {
            text = value
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#1A1A1A"))
            gravity = Gravity.END
        }
        row.addView(lbl)
        row.addView(val_)
        return row
    }

    private fun buildInfoSection(header: String, body: String): LinearLayout {
        val section = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, 4, 0, 16)
        }
        val hdr = TextView(this).apply {
            text = header
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#2E7D32"))
            setPadding(0, 0, 0, 6)
        }
        val bdy = TextView(this).apply {
            text = body
            textSize = 14f
            setTextColor(Color.parseColor("#333333"))
            setLineSpacing(0f, 1.4f)
        }
        section.addView(hdr)
        section.addView(bdy)
        return section
    }

    private fun buildThinDivider(): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.parseColor("#F0F0F0"))
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1)
        }
    }

    private fun buildSpacerView(dp: Int): android.view.View {
        return android.view.View(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp)
        }
    }

    private fun getSeverityColor(severity: String): Int {
        return when (severity.lowercase()) {
            "healthy"  -> Color.parseColor("#2E7D32")
            "mild"     -> Color.parseColor("#FBC02D")
            "moderate" -> Color.parseColor("#FF9800")
            "severe"   -> Color.parseColor("#F44336")
            "critical" -> Color.parseColor("#B71C1C")
            else       -> Color.parseColor("#666666")
        }
    }

    private fun base64ToBitmap(base64: String): Bitmap? {
        return try {
            // Strip "data:image/jpeg;base64," prefix if present
            val cleanBase64 = base64.substringAfter(",").ifBlank { base64 }
            val bytes = Base64.decode(cleanBase64, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        } catch (e: Exception) {
            null
        }
    }

    private fun buildShareText(pred: PredictionResponse): String {
        return """
GreenScan Analysis Report
═══════════════════════════
Disease: ${pred.displayName}
Confidence: ${pred.confidence}%
Plant Health Score: ${pred.gsaMetrics.plantHealthScore}/100
Severity: ${pred.gsaMetrics.severityLevel}
Risk Level: ${pred.gsaMetrics.riskLevel}
Treatment Priority: ${pred.gsaMetrics.treatmentPriority}
Affected Region: ${pred.gsaMetrics.affectedAreaPct}%

Powered by GreenScan AI
https://greenscan-bot5.onrender.com
        """.trimIndent()
    }
}
