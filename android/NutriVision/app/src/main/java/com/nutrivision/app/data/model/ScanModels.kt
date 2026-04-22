package com.nutrivision.app.data.model

// Removed Parcelable and Serializable imports and inheritance

data class TextScanRequest(
    val text: String,
    val user_id: String,
    val product_name: String? = null
)

data class ScanResponse(
    val scan_id: String?,
    val status: String?,
    val product_name: String?,
    val extracted_text: String?, // Keeping this for now, but AI won't use mock data
    val health_score: Float,
    val ingredients: List<IngredientResponse> = emptyList(),
    val recommendations: List<RecommendationItem> = emptyList(),
    val allergens: List<String>? = null,
    val dietary_suitability: DietarySuitability? = null,
    val nutrition: Nutrition? = null,
    val scan_type: String? = null,
    val status_message: String? = null
)

data class IngredientResponse(
    val match_confidence: Float?,
    val nutrition_source: String?,
    val matched_name: String?,
    val matched_type: String?
)

data class RecommendationItem(
    val type: String?,
    val title: String,
    val message: String,
    val severity: String
)

data class DietarySuitability(
    val is_dairy_free: Boolean? = null,
    val is_gluten_free: Boolean? = null,
    val is_keto_friendly: Boolean? = null,
    val is_nut_free: Boolean? = null,
    val is_vegan: Boolean? = null,
    val is_vegetarian: Boolean? = null
)

data class Nutrition(
    val carbohydrates: NutrientInfo? = null,
    val cholesterol: NutrientInfo? = null,
    val fat: NutrientInfo? = null,
    val fiber: NutrientInfo? = null,
    val protein: NutrientInfo? = null,
    val saturated_fat: NutrientInfo? = null,
    val sodium: NutrientInfo? = null,
    val sugar: NutrientInfo? = null,
    val total_calories: Double? = null
)

data class NutrientInfo(
    val daily_pct: Double? = null,
    val unit: String?,
    val value: Double? = null
)

data class UserProfile(
    val uid: String,
    val name: String,
    val email: String,
    val dietary_preferences: List<String>,
    val allergies: List<String>
)

data class UserProfileUpdate(
    val name: String? = null,
    val dietary_preferences: List<String>? = null,
    val allergies: List<String>? = null
)
