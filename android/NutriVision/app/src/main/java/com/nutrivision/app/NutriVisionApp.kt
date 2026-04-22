package com.nutrivision.app

import android.app.Application
import com.google.firebase.FirebaseApp

class NutriVisionApp : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)
    }
}