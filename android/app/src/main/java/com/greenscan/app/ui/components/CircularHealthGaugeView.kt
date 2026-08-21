package com.greenscan.app.ui.components

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import kotlin.math.min

class CircularHealthGaugeView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var score: Int = 100
    private var maxScore: Int = 100

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 32f
        color = Color.parseColor("#E0E0E0")
        strokeCap = Paint.Cap.ROUND
    }

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 36f
        strokeCap = Paint.Cap.ROUND
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 84f
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
    }

    private val subTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 32f
        color = Color.GRAY
        textAlign = Paint.Align.CENTER
    }

    private val rectF = RectF()

    fun setScore(newScore: Int) {
        this.score = newScore.coerceIn(0, 100)
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val size = min(width, height)
        val padding = 48f
        rectF.set(padding, padding, size - padding, size - padding)

        // Draw background arc (240 degrees arc)
        val startAngle = 150f
        val sweepAngle = 240f
        canvas.drawArc(rectF, startAngle, sweepAngle, false, backgroundPaint)

        // Determine color based on health score
        val progressColor = when {
            score >= 90 -> Color.parseColor("#2E7D32") // Green
            score >= 70 -> Color.parseColor("#FBC02D") // Yellow
            score >= 40 -> Color.parseColor("#F57C00") // Orange
            else -> Color.parseColor("#D32F2F")        // Red
        }

        progressPaint.color = progressColor
        textPaint.color = progressColor

        val currentSweep = (score.toFloat() / maxScore.toFloat()) * sweepAngle
        canvas.drawArc(rectF, startAngle, currentSweep, false, progressPaint)

        // Draw Center Score Text
        val centerX = width / 2f
        val centerY = height / 2f - 10f
        canvas.drawText("$score/100", centerX, centerY, textPaint)
        canvas.drawText("Health Score", centerX, centerY + 50f, subTextPaint)
    }
}
