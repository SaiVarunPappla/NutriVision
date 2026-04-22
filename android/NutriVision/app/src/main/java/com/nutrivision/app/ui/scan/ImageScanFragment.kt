package com.nutrivision.app.ui.scan

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.google.firebase.auth.FirebaseAuth
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.Text
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.nutrivision.app.R
import com.nutrivision.app.ui.ai.viewmodel.SharedScanResultViewModel
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean
import android.widget.ImageView
import com.google.android.material.button.MaterialButton

class ImageScanFragment : Fragment(R.layout.fragment_image_scan) {

    private enum class ScanUiMode {
        LIVE_PREVIEW,
        CAPTURED_IMAGE
    }

    private val viewModel: ImageScanViewModel by viewModels()
    private val sharedViewModel: SharedScanResultViewModel by activityViewModels()

    private var selectedImageUri: Uri? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private var imageCapture: ImageCapture? = null
    private var latestSuggestedProductName: String? = null
    private var latestLabelAreaRatio: Float = 0f
    private var latestIsSharp: Boolean = false
    private var hasWeakLiveQualityHint: Boolean = false
    private var uiMode: ScanUiMode = ScanUiMode.LIVE_PREVIEW
    private val frameAnalysisBusy = AtomicBoolean(false)

    private lateinit var previewView: PreviewView
    private lateinit var ivCapturedPreview: ImageView
    private lateinit var btnAnalyze: MaterialButton
    private lateinit var btnGallery: MaterialButton
    private lateinit var btnCamera: MaterialButton
    private lateinit var progressBar: ProgressBar
    private lateinit var tvCaptureHint: TextView
    private lateinit var tvScanStatus: TextView

    private lateinit var cameraExecutor: ExecutorService

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    private val blurVarianceThreshold = 95.0
    private val minLabelCoverageRatio = 0.22f

    private val galleryLauncher =
        registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
            Log.d("ImageScanFragment", "Gallery returned URI: $uri")
            uri?.let { handleImageSelection(it) }
        }

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
            Log.d("ImageScanFragment", "Camera permission granted: $isGranted")
            if (isGranted) {
                startCameraPreview()
            } else {
                Toast.makeText(
                    requireContext(),
                    "Camera permission is required to take photos.",
                    Toast.LENGTH_LONG
                ).show()
                setUiState(false)
            }
        }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        previewView = view.findViewById(R.id.previewView)
        ivCapturedPreview = view.findViewById(R.id.ivCapturedPreview)
        btnAnalyze = view.findViewById(R.id.btnAnalyze)
        btnGallery = view.findViewById(R.id.btnGallery)
        btnCamera = view.findViewById(R.id.btnCamera)
        progressBar = view.findViewById(R.id.progressBarScan)
        tvCaptureHint = view.findViewById(R.id.tvCaptureHint)
        tvScanStatus = view.findViewById(R.id.tvScanStatus)

        cameraExecutor = Executors.newSingleThreadExecutor()

        btnAnalyze.isEnabled = false

        btnGallery.setOnClickListener {
            galleryLauncher.launch("image/*")
        }

        btnCamera.setOnClickListener {
            if (selectedImageUri == null) {
                capturePhoto()
            } else {
                switchToLivePreviewMode(clearSelection = true)
            }
        }

        btnAnalyze.setOnClickListener {
            val uri = selectedImageUri
            if (uri == null) {
                Toast.makeText(
                    requireContext(),
                    "Please select or capture an image first.",
                    Toast.LENGTH_SHORT
                ).show()
                return@setOnClickListener
            }
            runMlKitAndUpload(uri)
        }

        viewModel.isLoading.observe(viewLifecycleOwner) { loading ->
            setUiState(loading)
            if (loading) {
                tvScanStatus.text = "Analyzing image..."
            }
        }

        viewModel.scanResponse.observe(viewLifecycleOwner) { response ->
            response?.let {
                Log.d("ImageScanFragment", "Scan success: ${it.scan_id}")
                tvScanStatus.text = ""
                sharedViewModel.setScanResponse(it)
                findNavController().navigate(R.id.action_nav_scan_to_nav_result)
            }
        }

        viewModel.errorMessage.observe(viewLifecycleOwner) { error ->
            error?.let {
                Log.e("ImageScanFragment", "Scan error: $it")
                Toast.makeText(requireContext(), it, Toast.LENGTH_LONG).show()
                tvScanStatus.text = "Scan failed. Please retake for better accuracy."
                setUiState(false)
            }
        }

        checkCameraPermissionAndLaunch()
    }

    private fun setUiState(isLoading: Boolean) {
        progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        val hasImage = selectedImageUri != null
        btnAnalyze.isEnabled = !isLoading && hasImage
        btnGallery.isEnabled = !isLoading
        btnCamera.isEnabled = !isLoading
        btnAnalyze.text = if (isLoading) "Analyzing..." else "Analyze"
        btnAnalyze.alpha = if (btnAnalyze.isEnabled) 1f else 0.65f
        btnGallery.alpha = if (btnGallery.isEnabled) 1f else 0.65f
        btnCamera.alpha = if (btnCamera.isEnabled) 1f else 0.65f
        if (!isLoading && tvScanStatus.text.toString() == "Analyzing image...") {
            tvScanStatus.text = ""
        }
    }

    private fun handleImageSelection(uri: Uri) {
        try {
            selectedImageUri = uri
            ivCapturedPreview.setImageURI(uri)
            uiMode = ScanUiMode.CAPTURED_IMAGE
            applyUiMode()
            btnCamera.text = "Retake"
            btnAnalyze.isEnabled = true
            tvCaptureHint.text = "Image ready. Tap Analyze to continue."
            tvScanStatus.text = if (hasWeakLiveQualityHint) {
                "Low confidence scan. Retake for better accuracy."
            } else {
                ""
            }
            setUiState(false)
            Log.d("ImageScanFragment", "Image selected successfully: $uri")
        } catch (e: Exception) {
            Log.e("ImageScanFragment", "Failed to handle selected image", e)
            Toast.makeText(requireContext(), "Failed to open image.", Toast.LENGTH_LONG).show()
            setUiState(false)
        }
    }

    private fun checkCameraPermissionAndLaunch() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                startCameraPreview()
            }
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                Toast.makeText(
                    requireContext(),
                    "Camera permission is required to take photos.",
                    Toast.LENGTH_LONG
                ).show()
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun startCameraPreview() {
        val providerFuture = ProcessCameraProvider.getInstance(requireContext())
        providerFuture.addListener({
            cameraProvider = providerFuture.get()
            bindCameraUseCases()
            if (uiMode == ScanUiMode.LIVE_PREVIEW) {
                applyUiMode()
            }
        }, ContextCompat.getMainExecutor(requireContext()))
    }

    private fun applyUiMode() {
        when (uiMode) {
            ScanUiMode.LIVE_PREVIEW -> {
                previewView.visibility = View.VISIBLE
                ivCapturedPreview.visibility = View.GONE
                btnCamera.text = "Capture"
                btnAnalyze.isEnabled = false
                previewView.alpha = 0f
                previewView.animate().alpha(1f).setDuration(180).start()
            }
            ScanUiMode.CAPTURED_IMAGE -> {
                previewView.visibility = View.GONE
                ivCapturedPreview.visibility = View.VISIBLE
                btnCamera.text = "Retake"
                btnAnalyze.isEnabled = selectedImageUri != null
                ivCapturedPreview.alpha = 0f
                ivCapturedPreview.animate().alpha(1f).setDuration(180).start()
            }
        }
    }

    private fun switchToLivePreviewMode(clearSelection: Boolean) {
        if (clearSelection) {
            selectedImageUri = null
            latestSuggestedProductName = null
            hasWeakLiveQualityHint = false
            tvScanStatus.text = ""
        }
        uiMode = ScanUiMode.LIVE_PREVIEW
        tvCaptureHint.text = "Align the product label inside the frame and keep steady."
        applyUiMode()
    }

    private fun bindCameraUseCases() {
        val provider = cameraProvider ?: return

        val preview = Preview.Builder().build().also {
            it.setSurfaceProvider(previewView.surfaceProvider)
        }

        imageCapture = ImageCapture.Builder()
            .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
            .build()

        val imageAnalysis = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()

        imageAnalysis.setAnalyzer(cameraExecutor) { imageProxy ->
            analyzePreviewFrame(imageProxy)
        }

        provider.unbindAll()
        provider.bindToLifecycle(
            viewLifecycleOwner,
            CameraSelector.DEFAULT_BACK_CAMERA,
            preview,
            imageCapture,
            imageAnalysis
        )
    }

    private fun analyzePreviewFrame(imageProxy: ImageProxy) {
        if (uiMode != ScanUiMode.LIVE_PREVIEW) {
            imageProxy.close()
            return
        }

        if (frameAnalysisBusy.getAndSet(true)) {
            imageProxy.close()
            return
        }

        val sharpness = estimateLumaVariance(imageProxy)
        val sharpEnough = sharpness >= blurVarianceThreshold

        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            frameAnalysisBusy.set(false)
            imageProxy.close()
            return
        }

        val inputImage = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
        recognizer.process(inputImage)
            .addOnSuccessListener { result ->
                val (candidateName, areaRatio) = selectLargestProductLikeBlock(result, inputImage.width, inputImage.height)
                latestSuggestedProductName = candidateName
                latestLabelAreaRatio = areaRatio
                latestIsSharp = sharpEnough
                hasWeakLiveQualityHint = !sharpEnough || areaRatio < minLabelCoverageRatio

                val hint = when {
                    !sharpEnough -> "Image is blurry. Hold steady or tap retake."
                    areaRatio < minLabelCoverageRatio -> "Move closer so the label fills most of the frame."
                    candidateName.isNullOrBlank() -> "Center the product name in frame."
                    else -> "Ready to capture."
                }

                requireActivity().runOnUiThread {
                    if (uiMode == ScanUiMode.LIVE_PREVIEW) {
                        tvCaptureHint.text = hint
                    }
                }
            }
            .addOnFailureListener {
                latestIsSharp = sharpEnough
            }
            .addOnCompleteListener {
                frameAnalysisBusy.set(false)
                imageProxy.close()
            }
    }

    private fun estimateLumaVariance(imageProxy: ImageProxy): Double {
        val yPlane = imageProxy.planes.firstOrNull() ?: return 0.0
        val buffer = yPlane.buffer
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)
        if (bytes.isEmpty()) return 0.0

        val step = (bytes.size / 6000).coerceAtLeast(1)
        var sum = 0.0
        var count = 0
        var i = 0
        while (i < bytes.size) {
            sum += (bytes[i].toInt() and 0xFF)
            count++
            i += step
        }
        if (count == 0) return 0.0

        val mean = sum / count
        var variance = 0.0
        i = 0
        while (i < bytes.size) {
            val diff = (bytes[i].toInt() and 0xFF) - mean
            variance += diff * diff
            i += step
        }

        return variance / count
    }

    private fun selectLargestProductLikeBlock(
        result: Text,
        imageWidth: Int,
        imageHeight: Int
    ): Pair<String?, Float> {
        var bestText: String? = null
        var bestArea = 0

        for (block in result.textBlocks) {
            val bbox = block.boundingBox ?: continue
            val text = block.text.replace("\n", " ").trim()
            if (text.isBlank() || looksLikeGarbage(text)) continue

            val area = bbox.width() * bbox.height()
            if (area > bestArea) {
                bestArea = area
                bestText = text.take(80)
            }
        }

        val totalArea = (imageWidth * imageHeight).coerceAtLeast(1)
        val ratio = bestArea.toFloat() / totalArea.toFloat()
        return Pair(bestText, ratio)
    }

    private fun capturePhoto() {
        val capture = imageCapture
        if (capture == null) {
            Toast.makeText(requireContext(), "Camera is not ready yet.", Toast.LENGTH_SHORT).show()
            return
        }

        val photoFile = createTempImageFile()
        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        capture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(requireContext()),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                    val fileUri = Uri.fromFile(photoFile)
                    handleImageSelection(fileUri)
                    if (!latestIsSharp || latestLabelAreaRatio < minLabelCoverageRatio) {
                        tvScanStatus.text = "Low confidence scan. Retake for better accuracy."
                    }
                }

                override fun onError(exception: ImageCaptureException) {
                    Toast.makeText(
                        requireContext(),
                        "Capture failed: ${exception.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        )
    }

    private fun createTempImageFile(): File {
        val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val storageDir = File(requireContext().cacheDir, "camera_scans").apply {
            if (!exists()) mkdirs()
        }
        return File.createTempFile("NutriVision_${timeStamp}_", ".jpg", storageDir)
    }

    private fun runMlKitAndUpload(uri: Uri) {
        try {
            setUiState(true)

            val image = InputImage.fromFilePath(requireContext(), uri)
            recognizer.process(image)
                .addOnSuccessListener { result ->
                    val recognizedText = result.text.trim()
                    val textDensity = recognizedText.length
                    val (_, areaRatio) = selectLargestProductLikeBlock(result, image.width, image.height)
                    val lowConfidence = textDensity < 25 || areaRatio < minLabelCoverageRatio

                    if (recognizedText.isBlank()) {
                        Toast.makeText(requireContext(), "No label text found. Please retake with better lighting.", Toast.LENGTH_LONG).show()
                        setUiState(false)
                        return@addOnSuccessListener
                    }

                    val (largestBlockName, _) = selectLargestProductLikeBlock(result, image.width, image.height)
                    val productName = largestBlockName
                        ?: latestSuggestedProductName
                        ?: deriveProductName(recognizedText)
                    val actualUserId = FirebaseAuth.getInstance().currentUser?.uid
                    if (actualUserId.isNullOrBlank()) {
                        Toast.makeText(requireContext(), "Please login before scanning.", Toast.LENGTH_LONG).show()
                        setUiState(false)
                        return@addOnSuccessListener
                    }

                    Log.d(
                        "ImageScanFragment",
                        "ML Kit extracted text length=${recognizedText.length}, productName=$productName"
                    )

                    if (lowConfidence) {
                        tvScanStatus.text = "Low-confidence OCR detected (label area/clarity). You can retake for better results."
                    } else {
                        tvScanStatus.text = ""
                    }

                    viewModel.uploadRecognizedText(
                        text = recognizedText,
                        userId = actualUserId,
                        productName = productName
                    )
                }
                .addOnFailureListener { e ->
                    Log.e("ImageScanFragment", "ML Kit recognition failed", e)
                    Toast.makeText(
                        requireContext(),
                        "Text recognition failed: ${e.message}",
                        Toast.LENGTH_LONG
                    ).show()
                    setUiState(false)
                }
        } catch (e: Exception) {
            Log.e("ImageScanFragment", "Failed to process image with ML Kit", e)
            Toast.makeText(
                requireContext(),
                "Failed to process image: ${e.message}",
                Toast.LENGTH_LONG
            ).show()
            setUiState(false)
        }
    }

    private fun deriveProductName(recognizedText: String): String? {
        val lines = recognizedText
            .lines()
            .map { it.trim() }
            .filter { it.isNotBlank() }

        if (lines.isEmpty()) return null

        val firstGoodLine = lines.firstOrNull { !looksLikeGarbage(it) }
        return firstGoodLine?.take(60) ?: "Scanned Food Product"
    }

    private fun looksLikeGarbage(line: String): Boolean {
        val clean = line.trim()
        if (clean.length !in 4..50) return true
        if (clean.count { it.isLetter() } < 3) return true
        if (clean.contains(",")) return true
        if (clean.contains("(") || clean.contains(")")) return true

        val lower = clean.lowercase(Locale.ROOT)
        if (lower.startsWith("ingredients") || lower.startsWith("ingredient:")) return true
        if (lower.startsWith("nutrition")) return true
        if (lower.startsWith("serving")) return true

        return false
    }

    override fun onDestroyView() {
        super.onDestroyView()
        cameraProvider?.unbindAll()
        cameraExecutor.shutdown()
        recognizer.close()
    }
}