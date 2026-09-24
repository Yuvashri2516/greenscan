package com.greenscan.app.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/**
 * LoginActivity — Routes directly to MainActivity.
 * GreenScan does not require user accounts; authentication is optional.
 */
class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // No login required — navigate directly to main app
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
