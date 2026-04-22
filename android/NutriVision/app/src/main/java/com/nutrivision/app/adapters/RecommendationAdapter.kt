package com.nutrivision.app.adapters

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.nutrivision.app.R
import com.nutrivision.app.data.model.RecommendationItem

class RecommendationAdapter(private val items: List<RecommendationItem>) : 
    RecyclerView.Adapter<RecommendationAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.tvRecTitle)
        val message: TextView = view.findViewById(R.id.tvRecMessage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_recommendation, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.title.text = item.title
        holder.message.text = item.message
        
        if (item.severity == "high") {
            holder.title.setTextColor(Color.RED)
        } else {
            holder.title.setTextColor(Color.DKGRAY)
        }
    }

    override fun getItemCount() = items.size
}
