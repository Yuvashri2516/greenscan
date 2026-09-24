package com.greenscan.app.ui

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.animation.AccelerateDecelerateInterpolator
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Programmatic splash layout — no R.layout dependency
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.parseColor("#1B5E20"))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.MATCH_PARENT
            )
        }

        val emojiView = TextView(this).apply {
            text = "🌿"
            textSize = 80f
            gravity = Gravity.CENTER
            alpha = 0f
        }

        val titleView = TextView(this).apply {
            text = "GreenScan"
            textSize = 42f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            alpha = 0f
            letterSpacing = 0.05f
        }

        val taglineView = TextView(this).apply {
            text = "AI Plant Health Detection"
            textSize = 16f
            setTextColor(Color.parseColor("#A5D6A7"))
            gravity = Gravity.CENTER
            alpha = 0f
            setPadding(0, 16, 0, 0)
        }

        val poweredView = TextView(this).apply {
            text = "Powered by EfficientNet-B0 · Grad-CAM · GSA"
            textSize = 11f
            setTextColor(Color.parseColor("#66BB6A"))
            gravity = Gravity.CENTER
            alpha = 0f
            setPadding(0, 48, 0, 0)
        }

        root.addView(emojiView)
        root.addView(titleView)
        root.addView(taglineView)
        root.addView(poweredView)
        setContentView(root)

        // Animate elements in sequence
        val fadeInEmoji = ObjectAnimator.ofFloat(emojiView, "alpha", 0f, 1f).apply {
            duration = 600
            interpolator = AccelerateDecelerateInterpolator()
        }
        val scaleXEmoji = ObjectAnimator.ofFloat(emojiView, "scaleX", 0.5f, 1f).apply { duration = 600 }
        val scaleYEmoji = ObjectAnimator.ofFloat(emojiView, "scaleY", 0.5f, 1f).apply { duration = 600 }

        val fadeInTitle = ObjectAnimator.ofFloat(titleView, "alpha", 0f, 1f).apply {
            duration = 600
            startDelay = 300
        }
        val slideTitle = ObjectAnimator.ofFloat(titleView, "translationY", 40f, 0f).apply {
            duration = 600
            startDelay = 300
        }

        val fadeInTagline = ObjectAnimator.ofFloat(taglineView, "alpha", 0f, 1f).apply {
            duration = 500
            startDelay = 700
        }
        val fadeInPowered = ObjectAnimator.ofFloat(poweredView, "alpha", 0f, 1f).apply {
            duration = 500
            startDelay = 1000
        }

        val animSet = AnimatorSet()
        animSet.playTogether(
            fadeInEmoji, scaleXEmoji, scaleYEmoji,
            fadeInTitle, slideTitle,
            fadeInTagline, fadeInPowered
        )
        animSet.start()

        // Navigate to MainActivity after 2.5 seconds
        Handler(Looper.getMainLooper()).postDelayed({
            startActivity(Intent(this, MainActivity::class.java))
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
            finish()
        }, 2500)
    }
}
