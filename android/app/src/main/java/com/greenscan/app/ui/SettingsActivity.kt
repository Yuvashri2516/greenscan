package com.greenscan.app.ui

import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            val t = TextView(context).apply {
                text = "⚙️ Settings & Preferences"
                textSize = 22f
                setTypeface(null, android.graphics.Typeface.BOLD)
            }
            addView(t)
        }
        setContentView(layout)
    }
}
