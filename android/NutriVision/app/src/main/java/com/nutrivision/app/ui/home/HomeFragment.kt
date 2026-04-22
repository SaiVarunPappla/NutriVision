package com.nutrivision.app.ui.home

import android.os.Bundle
import android.view.View
import android.view.animation.AnimationUtils
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.nutrivision.app.R

class HomeFragment : Fragment(R.layout.fragment_home) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val enterAnim = AnimationUtils.loadAnimation(requireContext(), R.anim.fade_slide_up)
        listOf(
            R.id.cardScanImage,
            R.id.cardAskAi,
            R.id.cardTypeIngredients,
            R.id.cardHistory,
        ).forEachIndexed { idx, id ->
            view.findViewById<View>(id).apply {
                alpha = 0f
                postDelayed({
                    startAnimation(enterAnim)
                    alpha = 1f
                }, (idx * 40).toLong())
            }
        }
        
        view.findViewById<View>(R.id.cardScanImage).setOnClickListener {
            findNavController().navigate(R.id.action_nav_home_to_nav_scan)
        }
        
        view.findViewById<View>(R.id.cardTypeIngredients).setOnClickListener {
            findNavController().navigate(R.id.action_nav_home_to_nav_text_input)
        }

        view.findViewById<View>(R.id.cardAskAi).setOnClickListener {
            findNavController().navigate(R.id.action_nav_home_to_nav_chatbot)
        }

        view.findViewById<View>(R.id.cardHistory).setOnClickListener {
            findNavController().navigate(R.id.nav_history)
        }
    }
}
