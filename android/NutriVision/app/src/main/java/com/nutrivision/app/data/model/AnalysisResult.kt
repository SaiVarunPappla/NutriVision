package com.nutrivision.app.data.model

data class AnalysisResult(
    val scanResponse: ScanResponse?,
    val errorMessage: String?,
    val statusMessage: String? // To hold backend status messages
)
