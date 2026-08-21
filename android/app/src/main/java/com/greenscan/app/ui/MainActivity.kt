package com.greenscan.app.ui

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.greenscan.app.R
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {

    private val galleryLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val imageUri: Uri? = result.data?.data
            imageUri?.let { uri ->
                val tempFile = uriToFile(uri)
                if (tempFile != null) {
                    val intent = Intent(this, ScanningActivity::class.java).apply {
                        putExtra("IMAGE_PATH", tempFile.absolutePath)
                    }
                    startActivity(intent)
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(createHomeLayout())
    }

    private fun createHomeLayout(): LinearLayout {
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            setBackgroundColor(android.graphics.Color.parseColor("#F4F6F8"))
        }

        // Header Title
        val titleView = android.widget.TextView(this).apply {
            text = "🌿 GreenScan"
            textSize = 28f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(android.graphics.Color.parseColor("#1B5E20"))
        }

        val subTitleView = android.widget.TextView(this).apply {
            text = "AI Agricultural Decision Support System"
            textSize = 14f
            setTextColor(android.graphics.Color.parseColor("#555555"))
            setPadding(0, 8, 0, 48)
        }

        layout.addView(titleView)
        layout.addView(subTitleView)

        // 1. Capture Leaf Button
        val btnCapture = createActionButton("📷 Capture Leaf", "#2E7D32") {
            startActivity(Intent(this, CameraActivity::class.java))
        }

        // 2. Upload Leaf Button
        val btnUpload = createActionButton("🖼️ Upload Leaf from Gallery", "#1976D2") {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            galleryLauncher.launch(intent)
        }

        // 3. Scan History Button
        val btnHistory = createActionButton("📜 Scan History", "#388E3C") {
            startActivity(Intent(this, HistoryActivity::class.java))
        }

        // 4. Disease Library Button
        val btnLibrary = createActionButton("📚 Disease Library", "#F57C00") {
            startActivity(Intent(this, RecommendationActivity::class.java))
        }

        // 5. AI Chatbot Button
        val btnChat = createActionButton("🤖 AI Agricultural Chatbot", "#7B1FA2") {
            startActivity(Intent(this, ChatbotActivity::class.java))
        }

        layout.addView(btnCapture)
        layout.addView(btnUpload)
        layout.addView(btnHistory)
        layout.addView(btnLibrary)
        layout.addView(btnChat)

        return layout
    }

    private fun createActionButton(textStr: String, colorHex: String, onClick: () -> Unit): Button {
        return Button(this).apply {
            text = textStr
            textSize = 16f
            setTextColor(android.graphics.Color.WHITE)
            setBackgroundColor(android.graphics.Color.parseColor(colorHex))
            setPadding(32, 32, 32, 32)
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            params.setMargins(0, 16, 0, 16)
            layoutParams = params
            setOnClickListener { onClick() }
        }
    }

    private fun uriToFile(uri: Uri): File? {
        return try {
            val inputStream = contentResolver.openInputStream(uri) ?: return null
            val file = File(cacheDir, "upload_leaf_${System.currentTimeMillis()}.jpg")
            val outputStream = FileOutputStream(file)
            inputStream.copyTo(outputStream)
            inputStream.close()
            outputStream.close()
            file
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
