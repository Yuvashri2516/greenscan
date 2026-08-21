package com.greenscan.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.greenscan.app.data.ApiClient
import com.greenscan.app.data.AppDatabase
import com.greenscan.app.data.GreenScanRepository
import kotlinx.coroutines.launch
import java.io.File

class ScanningActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            setPadding(64, 64, 64, 64)
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        val statusText = TextView(this).apply {
            text = "🔬 Analyzing Leaf Sample..."
            textSize = 20f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
            setPadding(0, 0, 0, 32)
        }

        val progressBar = ProgressBar(this).apply {
            isIndeterminate = true
        }

        val subText = TextView(this).apply {
            text = "Performing OpenCV Enhancement -> EfficientNet-B0 -> Grad-CAM -> GSA Severity Analyzer"
            textSize = 13f
            setTextColor(android.graphics.Color.GRAY)
            setPadding(0, 32, 0, 0)
        }

        layout.addView(statusText)
        layout.addView(progressBar)
        layout.addView(subText)
        setContentView(layout)

        val imagePath = intent.getStringExtra("IMAGE_PATH")
        if (imagePath != null) {
            val file = File(imagePath)
            
            // Create Preview UI
            val previewLayout = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                gravity = android.view.Gravity.CENTER
                setPadding(48, 48, 48, 48)
                setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
            }
            
            val imageView = android.widget.ImageView(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 800
                ).apply { setMargins(0, 0, 0, 48) }
                scaleType = android.widget.ImageView.ScaleType.CENTER_CROP
                setImageURI(android.net.Uri.fromFile(file))
            }
            
            val scanBtn = android.widget.Button(this).apply {
                text = "✅ Confirm & Scan"
                setBackgroundColor(android.graphics.Color.parseColor("#2E7D32"))
                setTextColor(android.graphics.Color.WHITE)
                setOnClickListener {
                    setContentView(layout) // Show loading layout
                    processImage(file)
                }
            }
            
            val retakeBtn = android.widget.Button(this).apply {
                text = "🔄 Retake / Cancel"
                setBackgroundColor(android.graphics.Color.GRAY)
                setTextColor(android.graphics.Color.WHITE)
                setOnClickListener {
                    finish()
                }
            }
            
            previewLayout.addView(imageView)
            previewLayout.addView(scanBtn)
            previewLayout.addView(retakeBtn)
            
            setContentView(previewLayout)
            
        } else {
            Toast.makeText(this, "No image file found", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    private fun processImage(file: File) {
        lifecycleScope.launch {
            val db = AppDatabase.getDatabase(applicationContext)
            val repository = GreenScanRepository(ApiClient.apiService, db.historyDao())
            val result = repository.predictLeafDisease(file)

            result.onSuccess { response ->
                val intent = Intent(this@ScanningActivity, DashboardActivity::class.java).apply {
                    putExtra("PREDICTION_DATA", response)
                }
                startActivity(intent)
                finish()
            }.onFailure { err ->
                Toast.makeText(this@ScanningActivity, "Analysis Error: ${err.message}", Toast.LENGTH_LONG).show()
                finish()
            }
        }
    }
}
