package com.nutrivision.app.ui.ai

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.animation.AnimationUtils
import android.view.inputmethod.EditorInfo
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.fragment.app.viewModels
import com.nutrivision.app.R
import com.google.android.material.button.MaterialButton
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.ui.ai.viewmodel.SharedScanResultViewModel
import com.nutrivision.app.ui.ai.viewmodel.ChatbotViewModel
import com.google.android.material.chip.Chip

class ChatbotFragment : Fragment() {

    private val sharedViewModel: SharedScanResultViewModel by activityViewModels()
    private val chatbotViewModel: ChatbotViewModel by viewModels()

    private var latestScanResponse: ScanResponse? = null

    private lateinit var etChatQuestion: EditText
    private lateinit var btnSendQuestion: MaterialButton
    private lateinit var progressChatLoading: ProgressBar
    private lateinit var tvChatbotResponse: TextView
    private lateinit var tvAiMode: TextView
    private lateinit var scrollAnswer: androidx.core.widget.NestedScrollView
    private lateinit var chipWeightLoss: Chip
    private lateinit var chipKids: Chip
    private lateinit var chipGym: Chip
    private lateinit var chipDiabetes: Chip
    private lateinit var chipExplainIngredients: Chip

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_chatbot, container, false)
        etChatQuestion = view.findViewById(R.id.etChatQuestion)
        btnSendQuestion = view.findViewById(R.id.btnSendQuestion)
        progressChatLoading = view.findViewById(R.id.progressChatLoading)
        tvChatbotResponse = view.findViewById(R.id.tvChatbotResponse)
        tvAiMode = view.findViewById(R.id.tvAiMode)
        scrollAnswer = view.findViewById(R.id.scrollAnswer)
        chipWeightLoss = view.findViewById(R.id.chipWeightLoss)
        chipKids = view.findViewById(R.id.chipKids)
        chipGym = view.findViewById(R.id.chipGym)
        chipDiabetes = view.findViewById(R.id.chipDiabetes)
        chipExplainIngredients = view.findViewById(R.id.chipExplainIngredients)
        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.scanResponse.observe(viewLifecycleOwner) { scanResponse ->
            latestScanResponse = scanResponse
            if (scanResponse != null) {
                tvAiMode.text = "Mode: Scan AI"
                tvChatbotResponse.text = "Hello! How can I help you with '${scanResponse.product_name}' today?"
            } else {
                tvAiMode.text = "Mode: General NutriVision AI"
                tvChatbotResponse.text = "No scan result available. You can still ask general nutrition questions."
            }
        }

        btnSendQuestion.setOnClickListener {
            sendCurrentQuestion()
        }

        etChatQuestion.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEND) {
                sendCurrentQuestion()
                true
            } else {
                false
            }
        }

        setupQuickPromptChips()

        chatbotViewModel.isLoading.observe(viewLifecycleOwner) { isLoading ->
            progressChatLoading.visibility = if (isLoading) View.VISIBLE else View.GONE
            btnSendQuestion.isEnabled = !isLoading
            btnSendQuestion.text = if (isLoading) "Thinking..." else "Ask NutriVision AI"
            btnSendQuestion.alpha = if (btnSendQuestion.isEnabled) 1f else 0.7f
        }

        chatbotViewModel.answer.observe(viewLifecycleOwner) { answer ->
            if (!answer.isNullOrBlank()) {
                tvChatbotResponse.text = answer
                tvChatbotResponse.startAnimation(
                    AnimationUtils.loadAnimation(requireContext(), R.anim.gentle_fade_in)
                )
                scrollAnswer.post {
                    scrollAnswer.fullScroll(View.FOCUS_DOWN)
                }
            }
        }

        chatbotViewModel.error.observe(viewLifecycleOwner) { err ->
            if (!err.isNullOrBlank()) {
                Toast.makeText(requireContext(), err, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setupQuickPromptChips() {
        chipWeightLoss.setOnClickListener { submitQuickPrompt("Is this good for weight loss?") }
        chipKids.setOnClickListener { submitQuickPrompt("Is this suitable for kids?") }
        chipGym.setOnClickListener { submitQuickPrompt("Is this a good option for gym and muscle goals?") }
        chipDiabetes.setOnClickListener { submitQuickPrompt("Is this diabetes-friendly?") }
        chipExplainIngredients.setOnClickListener { submitQuickPrompt("Please explain the ingredient quality and risks.") }
    }

    private fun submitQuickPrompt(prompt: String) {
        etChatQuestion.setText(prompt)
        etChatQuestion.setSelection(prompt.length)
        sendCurrentQuestion()
    }

    private fun sendCurrentQuestion() {
        chatbotViewModel.askQuestion(
            question = etChatQuestion.text?.toString().orEmpty(),
            scanResponse = latestScanResponse
        )
    }
}
