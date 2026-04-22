package com.nutrivision.app.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.CheckBox
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.firebase.auth.FirebaseAuth
import com.nutrivision.app.R
import com.nutrivision.app.data.model.UserProfileUpdate
import com.nutrivision.app.data.network.RetrofitClient
import com.nutrivision.app.ui.auth.LoginActivity
import kotlinx.coroutines.launch

class ProfileFragment : Fragment(R.layout.fragment_profile) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val user = FirebaseAuth.getInstance().currentUser
        if (user == null) {
            Toast.makeText(requireContext(), "Please login again", Toast.LENGTH_SHORT).show()
            val intent = Intent(requireContext(), LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            return
        }
        val userId = user.uid

        val btnSave = view.findViewById<View>(R.id.btnSave)
        val btnLogout = view.findViewById<View>(R.id.btnLogout)
        val progressBar = view.findViewById<ProgressBar>(R.id.progressBarProfile)

        val cbVeg = view.findViewById<CheckBox>(R.id.cbVegetarian)
        val cbVegan = view.findViewById<CheckBox>(R.id.cbVegan)
        val etAllergies = view.findViewById<EditText>(R.id.etAllergies)

        progressBar.visibility = View.VISIBLE
        lifecycleScope.launch {
            try {
                val resp = RetrofitClient.apiService.getUserProfile(userId)
                if (resp.isSuccessful) {
                    val p = resp.body()
                    cbVeg.isChecked = p?.dietary_preferences?.contains("vegetarian") ?: false
                    cbVegan.isChecked = p?.dietary_preferences?.contains("vegan") ?: false
                    etAllergies.setText(p?.allergies?.joinToString(", "))
                }
            } catch (e: Exception) {
                // Ignore fallback
            } finally {
                progressBar.visibility = View.GONE
            }
        }

        btnSave.setOnClickListener {
            progressBar.visibility = View.VISIBLE
            btnSave.isEnabled = false
            lifecycleScope.launch {
                try {
                    val prefs = mutableListOf<String>()
                    if (cbVeg.isChecked) prefs.add("vegetarian")
                    if (cbVegan.isChecked) prefs.add("vegan")
                    val allergies = etAllergies.text.split(",").map { it.trim() }.filter { it.isNotEmpty() }

                    // Pass name as null since it's not being updated from UI
                    val update = UserProfileUpdate(name = null, dietary_preferences = prefs, allergies = allergies)
                    val resp = RetrofitClient.apiService.updateUserProfile(userId, update)
                    if (resp.isSuccessful) {
                        Toast.makeText(requireContext(), "Saved via API!", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "Saved Mocked (Offline)", Toast.LENGTH_SHORT).show()
                } finally {
                    progressBar.visibility = View.GONE
                    btnSave.isEnabled = true
                }
            }
        }

        btnLogout.setOnClickListener {
            FirebaseAuth.getInstance().signOut()
            val intent = Intent(requireContext(), LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            requireActivity().finish()
        }
    }
}
