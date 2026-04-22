package com.nutrivision.app.data.model

data class HistoryItem(
    val id: String,
    val userId: String,
    val description: String,
    val timestamp: String,
    val rating: Float,
    val type: String
)
