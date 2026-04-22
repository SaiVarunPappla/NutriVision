package com.nutrivision.app.data.model

data class ChatRequest(
    val question: String,
    val scan_context: ChatScanContext? = null,
    val user_profile: ChatUserProfile? = null
)

data class ChatResponse(
    val answer: String,
    val source: String? = null,
    val used_scan_context: Boolean = false,
    val safety_note: String? = null
)

data class ChatScanContext(
    val product_name: String? = null,
    val matched_name: String? = null,
    val match_confidence: Float? = null,
    val ocr_text: String? = null,
    val ocr_confidence: Float? = null,
    val ingredients: List<String>? = null,
    val allergens: List<String>? = null,
    val dietary_suitability: ChatDietarySuitability? = null,
    val nutrition_summary: ChatNutritionSummary? = null,
    val health_score: Float? = null,
    val recommendations: List<String>? = null
)

data class ChatDietarySuitability(
    val vegetarian: Boolean? = null,
    val vegan: Boolean? = null,
    val gluten_free: Boolean? = null,
    val dairy_free: Boolean? = null,
    val keto_friendly: Boolean? = null,
    val nut_free: Boolean? = null
)

data class ChatNutritionSummary(
    val calories: Double? = null,
    val protein_g: Double? = null,
    val sugar_g: Double? = null,
    val fat_g: Double? = null
)

data class ChatUserProfile(
    val allergies: List<String>? = null,
    val dietary_preferences: List<String>? = null,
    val goals: List<String>? = null
)
