package com.greenscan.app.ui

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class AboutActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            val t = TextView(context).apply {
                text = "ℹ️ About GreenScan\n\nAn Explainable AI-Based Plant Disease Detection and Decision Support System using EfficientNet-B0 and Grad-CAM.\n\nResearch Grade IEEE / Scopus Standard Project."
                textSize = 16f
            }
            addView(t)
        }
        setContentView(layout)
    }
}
