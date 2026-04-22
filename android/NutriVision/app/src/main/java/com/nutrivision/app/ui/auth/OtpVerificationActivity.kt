package com.nutrivision.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.PhoneAuthProvider
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.SetOptions
import com.nutrivision.app.R
import com.nutrivision.app.ui.main.MainActivity

class OtpVerificationActivity : AppCompatActivity() {

    private lateinit var auth: FirebaseAuth
    private lateinit var db: FirebaseFirestore

    private var verificationId: String? = null
    private var phoneNumber: String? = null

    companion object {
        private const val TAG = "OtpVerificationActivity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_otp_verification)

        auth = FirebaseAuth.getInstance()
        db = FirebaseFirestore.getInstance()

        verificationId = intent.getStringExtra(PhoneLoginActivity.EXTRA_VERIFICATION_ID)
        phoneNumber = intent.getStringExtra(PhoneLoginActivity.EXTRA_PHONE_NUMBER)

        val tvSentTo = findViewById<TextView>(R.id.tvSentTo)
        val etOtpCode = findViewById<TextInputEditText>(R.id.etOtpCode)
        val btnVerifyOtp = findViewById<MaterialButton>(R.id.btnVerifyOtp)
        val tvResendOtp = findViewById<TextView>(R.id.tvResendOtp)
        val progressBar = findViewById<ProgressBar>(R.id.progressBar)
        findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener { finish() }

        tvSentTo.text = "Sent to ${phoneNumber ?: ""}"

        btnVerifyOtp.setOnClickListener {
            val code = etOtpCode.text?.toString()?.trim()?.replace("\\s".toRegex(), "").orEmpty()

            if (verificationId.isNullOrEmpty()) {
                Toast.makeText(
                    this,
                    "Verification ID missing. Please send OTP again.",
                    Toast.LENGTH_LONG
                ).show()
                return@setOnClickListener
            }

            if (code.length != 6 || !code.all { it.isDigit() }) {
                Toast.makeText(
                    this,
                    "Enter a valid 6-digit OTP",
                    Toast.LENGTH_LONG
                ).show()
                return@setOnClickListener
            }

            progressBar.visibility = View.VISIBLE
            btnVerifyOtp.isEnabled = false
            btnVerifyOtp.text = "Verifying..."

            val credential = PhoneAuthProvider.getCredential(verificationId!!, code)

            auth.signInWithCredential(credential)
                .addOnCompleteListener(this) { task ->
                    progressBar.visibility = View.GONE
                    btnVerifyOtp.isEnabled = true
                    btnVerifyOtp.text = getString(R.string.verify_otp_btn)

                    if (task.isSuccessful) {
                        val user = task.result?.user

                        if (user == null) {
                            Toast.makeText(
                                this,
                                "Login failed: user is null",
                                Toast.LENGTH_LONG
                            ).show()
                            return@addOnCompleteListener
                        }

                        saveUserInBackground(
                            uid = user.uid,
                            phone = user.phoneNumber ?: phoneNumber.orEmpty()
                        )

                        Toast.makeText(
                            this,
                            "Phone login successful",
                            Toast.LENGTH_SHORT
                        ).show()

                        startActivity(Intent(this, MainActivity::class.java).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                        })
                        finish()
                    } else {
                        Log.e(TAG, "signInWithCredential failed", task.exception)
                        Toast.makeText(
                            this,
                            task.exception?.localizedMessage ?: "Invalid OTP",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
        }

        tvResendOtp.setOnClickListener {
            finish()
        }
    }

    private fun saveUserInBackground(uid: String, phone: String) {
        val userData = hashMapOf(
            "uid" to uid,
            "phone" to phone,
            "name" to "Phone User",
            "email" to "",
            "lastLoginAt" to System.currentTimeMillis()
        )

        db.collection("users")
            .document(uid)
            .set(userData, SetOptions.merge())
            .addOnSuccessListener {
                Log.d(TAG, "User profile saved")
            }
            .addOnFailureListener { e ->
                Log.e(TAG, "User profile save failed", e)
            }
    }
}