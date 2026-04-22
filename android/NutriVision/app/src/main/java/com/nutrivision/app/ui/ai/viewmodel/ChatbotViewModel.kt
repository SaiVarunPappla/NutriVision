package com.nutrivision.app.ui.ai.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.nutrivision.app.data.model.ChatRequest
import com.nutrivision.app.data.model.ChatResponse
import com.nutrivision.app.data.model.ChatDietarySuitability
import com.nutrivision.app.data.model.ChatNutritionSummary
import com.nutrivision.app.data.model.ChatScanContext
import com.nutrivision.app.data.model.ChatUserProfile
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.data.network.RetrofitClient
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class ChatbotViewModel : ViewModel() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _answer = MutableLiveData<String>()
    val answer: LiveData<String> = _answer

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun askQuestion(question: String, scanResponse: ScanResponse?) {
        val trimmed = question.trim()
        if (trimmed.isEmpty()) {
            _error.value = "Please enter a question."
            return
        }

        _isLoading.postValue(true)
        _error.postValue(null)

        scope.launch {
            try {
                val request = ChatRequest(
                    question = trimmed,
                    scan_context = scanResponse?.toChatScanContext(),
                    user_profile = loadOptionalUserProfile()
                )

                val response = RetrofitClient.apiService.askChat(request)
                if (response.isSuccessful && response.body() != null) {
                    val body: ChatResponse = response.body()!!
                    _answer.postValue(body.answer)
                } else {
                    _answer.postValue(
                        "I could not get an AI response right now. Please try again in a moment."
                    )
                }
            } catch (_: Exception) {
                _answer.postValue(
                    "I could not get an AI response right now. Please try again in a moment."
                )
            } finally {
                _isLoading.postValue(false)
            }
        }
    }

    private suspend fun loadOptionalUserProfile(): ChatUserProfile? {
        val uid = FirebaseAuth.getInstance().currentUser?.uid ?: return null
        return try {
            val resp = RetrofitClient.apiService.getUserProfile(uid)
            if (!resp.isSuccessful) return null
            val body = resp.body() ?: return null
            ChatUserProfile(
                allergies = body.allergies.ifEmpty { null },
                dietary_preferences = body.dietary_preferences.ifEmpty { null },
                goals = null
            )
        } catch (_: Exception) {
            null
        }
    }

    private fun ScanResponse.toChatScanContext(): ChatScanContext {
        val firstIngredient = ingredients.firstOrNull()
        val ingredientNames = ingredients.mapNotNull { it.matched_name?.takeIf { name -> name.isNotBlank() } }
        val recommendationMessages = recommendations.map { it.message }

        return ChatScanContext(
            product_name = product_name,
            matched_name = firstIngredient?.matched_name,
            match_confidence = firstIngredient?.match_confidence,
            ocr_text = extracted_text,
            ocr_confidence = null,
            ingredients = ingredientNames.ifEmpty { null },
            allergens = allergens,
            dietary_suitability = dietary_suitability?.let {
                ChatDietarySuitability(
                    vegetarian = it.is_vegetarian,
                    vegan = it.is_vegan,
                    gluten_free = it.is_gluten_free,
                    dairy_free = it.is_dairy_free,
                    keto_friendly = it.is_keto_friendly,
                    nut_free = it.is_nut_free,
                )
            },
            nutrition_summary = nutrition?.let {
                ChatNutritionSummary(
                    calories = it.total_calories,
                    protein_g = it.protein?.value,
                    sugar_g = it.sugar?.value,
                    fat_g = it.fat?.value,
                )
            },
            health_score = health_score,
            recommendations = recommendationMessages.ifEmpty { null },
        )
    }

    override fun onCleared() {
        super.onCleared()
        scope.cancel()
    }
}
