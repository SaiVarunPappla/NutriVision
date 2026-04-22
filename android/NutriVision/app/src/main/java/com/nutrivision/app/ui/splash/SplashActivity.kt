package com.nutrivision.app.ui.splash

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.auth.FirebaseAuth
import com.nutrivision.app.R
import com.nutrivision.app.ui.auth.LoginActivity
import com.nutrivision.app.ui.main.MainActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen() // Add this before super.onCreate
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    Handler(Looper.getMainLooper()).postDelayed({
            val currentUser = FirebaseAuth.getInstance().currentUser
            if (currentUser != null) {
                // User is signed in, go to Main
                startActivity(Intent(this, MainActivity::class.java))
            } else {
                // No user is signed in, go to Login
                startActivity(Intent(this, LoginActivity::class.java))
            }
            finish()
        }, 2000)
    }
}