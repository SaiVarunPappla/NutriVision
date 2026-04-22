package com.nutrivision.app.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.nutrivision.app.R
import com.nutrivision.app.data.model.HistoryItem

class HistoryAdapter(private val items: List<HistoryItem>) : 
    RecyclerView.Adapter<HistoryAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.tvHistoryTitle)
        val score: TextView = view.findViewById(R.id.tvHistoryScore)
        val date: TextView = view.findViewById(R.id.tvHistoryDate)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_history, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.title.text = item.description
        holder.score.text = "Score: %.1f / 10".format(item.rating)
        holder.date.text = item.timestamp
    }

    override fun getItemCount() = items.size
}
