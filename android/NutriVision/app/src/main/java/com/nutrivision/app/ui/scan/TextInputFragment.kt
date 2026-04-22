package com.nutrivision.app.ui.scan

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.google.firebase.auth.FirebaseAuth
import com.google.android.material.button.MaterialButton
import com.nutrivision.app.R
import com.nutrivision.app.ui.ai.viewmodel.SharedScanResultViewModel

class TextInputFragment : Fragment() {

    private val viewModel: TextInputViewModel by viewModels()
    // Get the shared ViewModel
    private val sharedViewModel: SharedScanResultViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_text_input, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val etIngredients = view.findViewById<EditText>(R.id.etIngredients)
        val btnAnalyze = view.findViewById<com.google.android.material.button.MaterialButton>(R.id.btnAnalyze)
        val progressBar = view.findViewById<ProgressBar>(R.id.progressBar)

        btnAnalyze.setOnClickListener {
            val input = etIngredients.text.toString().trim()
            val userId = FirebaseAuth.getInstance().currentUser?.uid

            if (input.isEmpty()) {
                etIngredients.error = "Please enter ingredients"
                return@setOnClickListener
            }
            if (userId == null) {
                Toast.makeText(context, "Please log in first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            progressBar.visibility = View.VISIBLE
            btnAnalyze.isEnabled = false

            viewModel.analyzeIngredients(input, userId)
        }

        viewModel.analysisResult.observe(viewLifecycleOwner) { result ->
            progressBar.visibility = View.GONE
            btnAnalyze.isEnabled = true

            if (result.scanResponse != null) {
                val message = result.statusMessage ?: "Analysis successful!"
                Toast.makeText(context, message, Toast.LENGTH_SHORT).show()

                // Save the ScanResponse to the SharedViewModel
                sharedViewModel.setScanResponse(result.scanResponse)

                // Navigate to ResultFragment without passing data in the bundle
                findNavController().navigate(R.id.action_nav_text_input_to_nav_result)
            } else {
                val displayError = "Analysis failed. ${result.errorMessage ?: "An unknown error occurred."}"
                Toast.makeText(context, displayError, Toast.LENGTH_LONG).show()
            }
        }
    }
}