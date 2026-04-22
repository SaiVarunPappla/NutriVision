package com.nutrivision.app.ui.history

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.firebase.auth.FirebaseAuth
import com.nutrivision.app.R
import com.nutrivision.app.adapters.HistoryAdapter
import com.nutrivision.app.data.model.HistoryItem
import com.nutrivision.app.data.network.RetrofitClient
import com.nutrivision.app.ui.auth.LoginActivity
import kotlinx.coroutines.launch

class HistoryFragment : Fragment(R.layout.fragment_history) {
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

        val rv = view.findViewById<RecyclerView>(R.id.rvHistory)
        val progressBar = view.findViewById<ProgressBar>(R.id.progressBarHistory)
        val tvEmptyHistory = view.findViewById<TextView>(R.id.tvEmptyHistory)
        rv.layoutManager = LinearLayoutManager(requireContext())

        progressBar.visibility = View.VISIBLE
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.getHistory(userId)
                if (response.isSuccessful && response.body() != null) {
                    val items = response.body()?.history ?: emptyList()
                    rv.adapter = HistoryAdapter(items)
                    tvEmptyHistory.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
                } else {
                    throw Exception("API Error")
                }
            } catch (e: Exception) {
                Toast.makeText(requireContext(), "Offline Mode History", Toast.LENGTH_SHORT).show()
                val fallback = listOf(HistoryItem("1", "s1", "Mocked Item", "2026-04-16", 7.0f, "text"))
                rv.adapter = HistoryAdapter(fallback)
                tvEmptyHistory.visibility = if (fallback.isEmpty()) View.VISIBLE else View.GONE
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }
}