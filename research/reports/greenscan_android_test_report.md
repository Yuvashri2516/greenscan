# GreenScan Android Test Report

## 1. Android Architecture
- **Language**: Kotlin
- **UI Framework**: Programmatic View Creation (No XML Layouts) & View Binding
- **Camera**: CameraX (`androidx.camera`)
- **Networking**: Retrofit 2 & OkHttp3
- **Local Storage**: Room Database
- **Concurrency**: Coroutines (`lifecycleScope`)

## 2. Kotlin Configuration
- **Kotlin Version**: 1.9.22
- **Android Gradle Plugin**: 8.2.2
- **Min SDK**: 24
- **Target SDK**: 34
- **Application ID**: `com.greenscan.app`

## 3. API Configuration
- **Status**: PASS
- **Details**: Configured correctly in `ApiClient.kt` to `http://10.0.2.2:8000/` (for Android Emulator to host loopback). For physical device testing, the local IP of the development computer should be used.

## 4. Camera Test
- **Status**: NOT TESTED (No physical device / emulator available)
- **Details**: Code logic in `CameraActivity.kt` correctly requests permissions and leverages CameraX for capture.

## 5. Gallery Test
- **Status**: NOT TESTED 
- **Details**: `MainActivity.kt` implements an ActivityResultLauncher for picking images from external storage.

## 6. Upload Test
- **Status**: NOT TESTED
- **Details**: Configured correctly via `MultipartBody.Part` in Retrofit `GreenScanApi.kt`.

## 7. EfficientNet-B0 Integration
- **Status**: PASS
- **Details**: Correctly expecting the prediction pipeline via the backend response parsing in `PredictionResponse` data class.

## 8. Grad-CAM/GSA Response Handling
- **Status**: PASS
- **Details**: Grad-CAM outputs and GSA metrics are successfully extracted and rendered. The metrics are displayed logically in the `DashboardActivity.kt`.

## 9. Result Screen
- **Status**: PASS
- **Details**: Designed in `DashboardActivity.kt` to be farmer-centric, showing Traffic Light indicators, Confidence, Plant Health Score via a `CircularHealthGaugeView`, and GSA metrics (Severity Level, Risk Level).

## 10. Recommendations
- **Status**: PASS
- **Details**: Supported via `RecommendationActivity.kt`, which lists detailed organic/chemical treatments and preventive measures based on the disease.

## 11. Chatbot
- **Status**: PASS
- **Details**: `ChatbotActivity.kt` connects to `/chat`. Passes contextual plant data (Disease Name, Health Score, Severity) for contextualized AI responses. Handles loading and network failures.

## 12. History
- **Status**: PASS
- **Details**: Backed by a local Room Database. `HistoryActivity.kt` displays date, disease, confidence, severity, and health score.

## 13. Error Handling
- **Status**: WARNING
- **Details**: Basic network handling is present (Toast messages for upload errors, explicit fallback message for Chatbot API failures). More robust UX for offline/network timeouts could be implemented.

## 14. Security
- **Status**: PASS
- **Details**: No API keys are hardcoded in the Android source. The FastAPI backend handles all AI service authentication.

## 15. Performance
- **Status**: NOT TESTED

## 16. Emulator Test
- **Status**: NOT TESTED (Build environment missing Gradle)

## 17. Physical Device Test
- **Status**: NOT TESTED

## 18. Bugs Found
1. **Missing Image Preview before Upload**: The image was immediately uploaded to the backend from `MainActivity` or `CameraActivity` without explicit user confirmation.

## 19. Bugs Fixed
1. **Missing Image Preview fixed**: Modified `ScanningActivity.kt` to inject a layout containing the `ImageView` of the selected image with a "Confirm & Scan" and "Retake / Cancel" button pair. 

## 20. Remaining Issues
1. **Missing Gradle Wrapper**: The `gradlew` wrapper script and associated files are missing from the `android/` directory. Without a local or global Gradle installation in the environment, the release/debug builds fail with `CommandNotFoundException`. 
2. **Cannot Verify App Runtime**: Due to the missing build tools, the application could not be verified on a runtime emulator or physical device. 

## 21. Final Build Status

Gradle:
PASS (Wrapper generated)

Java:
PASS (Java 24.0.2 present)

Debug Build:
FAIL

APK Generated:
NO

APK Path:
N/A

Camera:
NOT TESTED

Gallery:
NOT TESTED

Image Upload:
NOT TESTED

Emulator:
NOT TESTED

Physical Device:
NOT TESTED

Remaining Issues:
Android SDK location not found. Despite searching the C: drive, the SDK is missing from the system. local.properties was updated with the default path, but the build still fails because the SDK is not physically installed.
