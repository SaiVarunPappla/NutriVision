package com.nutrivision.app.ui.result

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.nutrivision.app.R
import com.nutrivision.app.adapters.RecommendationAdapter
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.ui.ai.viewmodel.SharedScanResultViewModel
import androidx.fragment.app.activityViewModels

class ResultFragment : Fragment(R.layout.fragment_result) {

    private lateinit var tvHealthScore: TextView
    private lateinit var tvProductName: TextView
    private lateinit var tvAllergens: TextView
    private lateinit var tvDietarySuitability: TextView
    private lateinit var llNutrition: LinearLayout
    private lateinit var rvRecommendations: RecyclerView
    private lateinit var rvIngredients: RecyclerView // This RecyclerView will be unused as IngredientAdapter is missing
    private lateinit var tvNoDataAvailable: TextView
    private lateinit var btnAskAi: TextView
    private lateinit var tvConfidenceBadge: TextView
    // Removed btnBack as it's not in fragment_result.xml

    // Use activityViewModels to share ViewModel across fragments in the same Activity
    private val sharedViewModel: SharedScanResultViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize UI elements
        tvHealthScore = view.findViewById(R.id.tvHealthScore)
        tvProductName = view.findViewById(R.id.tvProductName)
        tvAllergens = view.findViewById(R.id.tvAllergens)
        tvDietarySuitability = view.findViewById(R.id.tvDietarySuitability)
        llNutrition = view.findViewById(R.id.llNutrition)
        rvRecommendations = view.findViewById(R.id.rvRecommendations)
        rvIngredients = view.findViewById(R.id.rvIngredients) // Keep reference, but it won't be used
        tvNoDataAvailable = view.findViewById(R.id.tvNoDataAvailable)
        btnAskAi = view.findViewById(R.id.btnAskAi)
        tvConfidenceBadge = view.findViewById(R.id.tvConfidenceBadge)
        // btnBack removed

        // IngredientAdapter removed due to missing class
        // rvIngredients.adapter = ingredientAdapter // Removed
        rvIngredients.layoutManager = LinearLayoutManager(requireContext()) // Keep layout manager

        // Observe the ScanResponse from the shared ViewModel
        sharedViewModel.scanResponse.observe(viewLifecycleOwner) { response ->
            if (response != null) {
                displayScanResults(response)
                setupAiButton(response)
            } else {
                // Handle case where ScanResponse is null
                tvNoDataAvailable.visibility = View.VISIBLE
                // Removed reference to llScanDetails as it's not directly available and may cause issues
                // view.findViewById<LinearLayout>(R.id.llScanDetails).visibility = View.GONE
            }
        }

        view.findViewById<com.google.android.material.button.MaterialButton>(R.id.btnDone).setOnClickListener {
            findNavController().navigate(R.id.action_nav_result_to_nav_home)
        }

        // Setup back button listener - removed as btnBack is not in the layout
        // setupBackButton()
    }

    // Handle ingredient click - removed as IngredientAdapter is missing
    // private fun onIngredientClicked(ingredient: IngredientResponse) { ... }

    // Setup click listener for the "Ask NutriVision AI" button
    private fun setupAiButton(scanResponse: ScanResponse) {
        btnAskAi.setOnClickListener {
            // Navigate to ChatbotFragment
            // SharedViewModel already holds scanResponse, no need to pass it again via nav args
            findNavController().navigate(R.id.action_nav_result_to_nav_chatbot)
        }
    }

    private fun displayScanResults(response: ScanResponse) {
        tvNoDataAvailable.visibility = View.GONE
        // Removed reference to llScanDetails as it's not directly available and may cause issues
        // view?.findViewById<LinearLayout>(R.id.llScanDetails)?.visibility = View.VISIBLE

        // Product Name
        tvProductName.text = response.product_name ?: "N/A"
        renderConfidenceBadge(response)

        // Health Score
        tvHealthScore.text = "Health Score: %.1f / 10".format(response.health_score)

        // Ingredients List (if available)
        // Removed IngredientAdapter binding code
        if (!response.ingredients.isNullOrEmpty()) {
            view?.findViewById<TextView>(R.id.tvIngredientsLabel)?.visibility = View.VISIBLE
            rvIngredients.visibility = View.VISIBLE
            // ingredientAdapter.submitList(response.ingredients) // Removed
        } else {
            rvIngredients.visibility = View.GONE
            view?.findViewById<TextView>(R.id.tvIngredientsLabel)?.visibility = View.GONE
        }

        // Recommendations
        if (response.recommendations.isNotEmpty()) {
            view?.findViewById<TextView>(R.id.tvRecommendationsLabel)?.visibility = View.VISIBLE
            rvRecommendations.visibility = View.VISIBLE
            rvRecommendations.adapter = RecommendationAdapter(response.recommendations)
        } else {
            view?.findViewById<TextView>(R.id.tvRecommendationsLabel)?.visibility = View.GONE
            rvRecommendations.visibility = View.GONE
        }

        // Allergens
        if (!response.allergens.isNullOrEmpty() && response.allergens.firstOrNull() != null) {
            view?.findViewById<TextView>(R.id.tvAllergensLabel)?.visibility = View.VISIBLE
            tvAllergens.visibility = View.VISIBLE
            tvAllergens.text = response.allergens.joinToString(", ")
        } else {
            view?.findViewById<TextView>(R.id.tvAllergensLabel)?.visibility = View.GONE
            tvAllergens.visibility = View.GONE
        }

        // Dietary Suitability
        if (response.dietary_suitability != null) {
            view?.findViewById<TextView>(R.id.tvDietarySuitabilityLabel)?.visibility = View.VISIBLE
            tvDietarySuitability.visibility = View.VISIBLE
            val suitability = response.dietary_suitability
            val suitabilityText = buildString {
                append("Dairy-Free: ${suitability.is_dairy_free ?: "N/A"}\n")
                append("Gluten-Free: ${suitability.is_gluten_free ?: "N/A"}\n")
                append("Keto-Friendly: ${suitability.is_keto_friendly ?: "N/A"}\n")
                append("Nut-Free: ${suitability.is_nut_free ?: "N/A"}\n")
                append("Vegan: ${suitability.is_vegan ?: "N/A"}\n")
                append("Vegetarian: ${suitability.is_vegetarian ?: "N/A"}")
            }
            tvDietarySuitability.text = suitabilityText
        } else {
            view?.findViewById<TextView>(R.id.tvDietarySuitabilityLabel)?.visibility = View.GONE
            tvDietarySuitability.visibility = View.GONE
        }

        // Nutrition
        if (response.nutrition != null) {
            llNutrition.visibility = View.VISIBLE
            view?.findViewById<TextView>(R.id.tvNutritionLabel)?.visibility = View.VISIBLE

            val nutrition = response.nutrition
            val nutritionText = buildString {
                append("Calories: ${formatOneDecimal(nutrition.total_calories)}")
                append("\nFat: ${formatOneDecimal(nutrition.fat?.value)} g (${formatOneDecimal(nutrition.fat?.daily_pct)}%)")
                append("\nCarbs: ${formatOneDecimal(nutrition.carbohydrates?.value)} g (${formatOneDecimal(nutrition.carbohydrates?.daily_pct)}%)")
                append("\nProtein: ${formatOneDecimal(nutrition.protein?.value)} g (${formatOneDecimal(nutrition.protein?.daily_pct)}%)")
                append("\nSugar: ${formatOneDecimal(nutrition.sugar?.value)} g (${formatOneDecimal(nutrition.sugar?.daily_pct)}%)")
                append("\nSodium: ${formatOneDecimal(nutrition.sodium?.value)} mg (${formatOneDecimal(nutrition.sodium?.daily_pct)}%)")
            }
            view?.findViewById<TextView>(R.id.tvNutritionDetails)?.text = nutritionText
        } else {
            llNutrition.visibility = View.GONE
            view?.findViewById<TextView>(R.id.tvNutritionLabel)?.visibility = View.GONE
        }

        // Hide labels if no data is present for them
        if (response.ingredients.isNullOrEmpty()) { // Check for null or empty
            view?.findViewById<TextView>(R.id.tvIngredientsLabel)?.visibility = View.GONE
        }
        if (response.allergens.isNullOrEmpty()) {
            view?.findViewById<TextView>(R.id.tvAllergensLabel)?.visibility = View.GONE
        }
        if (response.dietary_suitability == null) {
            view?.findViewById<TextView>(R.id.tvDietarySuitabilityLabel)?.visibility = View.GONE
        }
        // Nutrition label visibility is handled within the nutrition block
    }

    private fun renderConfidenceBadge(response: ScanResponse) {
        val confidence = response.ingredients
            .mapNotNull { it.match_confidence }
            .maxOrNull()
            ?: 0f
        val pct = (confidence * 100f).coerceIn(0f, 100f)
        val tier = when {
            pct >= 80f -> "High"
            pct >= 60f -> "Medium"
            else -> "Low"
        }
        tvConfidenceBadge.text = "Confidence: $tier (${pct.toInt()}%)"
        tvConfidenceBadge.setTextColor(
            when (tier) {
                "High" -> resources.getColor(R.color.confidence_high, null)
                "Medium" -> resources.getColor(R.color.confidence_medium, null)
                else -> resources.getColor(R.color.confidence_low, null)
            }
        )
    }

    private fun formatOneDecimal(value: Float?): String {
        return if (value == null) "N/A" else "%.1f".format(value)
    }

    private fun formatOneDecimal(value: Double?): String {
        return if (value == null) "N/A" else "%.1f".format(value)
    }

    // Setup back button click - removed as btnBack is not in the layout
    // private fun setupBackButton() { btnBack.setOnClickListener { findNavController().navigateUp() } }
}