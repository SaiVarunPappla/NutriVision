package com.nutrivision.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.textfield.TextInputEditText
import com.google.firebase.FirebaseException
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.PhoneAuthCredential
import com.google.firebase.auth.PhoneAuthOptions
import com.google.firebase.auth.PhoneAuthProvider
import com.nutrivision.app.R
import java.util.concurrent.TimeUnit

class PhoneLoginActivity : AppCompatActivity() {

    private lateinit var auth: FirebaseAuth

    companion object {
        private const val TAG = "PhoneLoginActivity"
        const val EXTRA_VERIFICATION_ID = "verificationId"
        const val EXTRA_PHONE_NUMBER = "phoneNumber"
    }

    private val testNumbers = setOf(
        "+919603057838",
        "+919997955292"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_phone_login)

        auth = FirebaseAuth.getInstance()

        val etPhone = findViewById<TextInputEditText>(R.id.etPhoneNumber)
        val btnSendOtp = findViewById<MaterialButton>(R.id.btnSendOtp)
        val progressBar = findViewById<ProgressBar>(R.id.progressBar)
        findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener { finish() }

        btnSendOtp.setOnClickListener {
            val phoneNumber = etPhone.text?.toString()?.trim().orEmpty()

            if (!isValidPhone(phoneNumber)) {
                Toast.makeText(
                    this,
                    "Enter valid phone number with country code, e.g. +919876543210",
                    Toast.LENGTH_LONG
                ).show()
                return@setOnClickListener
            }

            progressBar.visibility = View.VISIBLE
            btnSendOtp.isEnabled = false
            btnSendOtp.text = "Sending..."

            if (testNumbers.contains(phoneNumber)) {
                auth.firebaseAuthSettings.setAppVerificationDisabledForTesting(true)
            }

            val callbacks = object : PhoneAuthProvider.OnVerificationStateChangedCallbacks() {

                override fun onVerificationCompleted(credential: PhoneAuthCredential) {
                    Log.d(TAG, "onVerificationCompleted called")
                    progressBar.visibility = View.GONE
                    btnSendOtp.isEnabled = true
                    btnSendOtp.text = getString(R.string.send_otp_btn)

                    Toast.makeText(
                        this@PhoneLoginActivity,
                        "Proceed with manual OTP entry.",
                        Toast.LENGTH_SHORT
                    ).show()
                }

                override fun onVerificationFailed(e: FirebaseException) {
                    Log.e(TAG, "onVerificationFailed", e)
                    progressBar.visibility = View.GONE
                    btnSendOtp.isEnabled = true
                    btnSendOtp.text = getString(R.string.send_otp_btn)

                    Toast.makeText(
                        this@PhoneLoginActivity,
                        e.localizedMessage ?: "Verification failed",
                        Toast.LENGTH_LONG
                    ).show()
                }

                override fun onCodeSent(
                    verificationId: String,
                    token: PhoneAuthProvider.ForceResendingToken
                ) {
                    Log.d(TAG, "onCodeSent: $verificationId")
                    progressBar.visibility = View.GONE
                    btnSendOtp.isEnabled = true
                    btnSendOtp.text = getString(R.string.send_otp_btn)

                    val intent = Intent(this@PhoneLoginActivity, OtpVerificationActivity::class.java)
                    intent.putExtra(EXTRA_VERIFICATION_ID, verificationId)
                    intent.putExtra(EXTRA_PHONE_NUMBER, phoneNumber)
                    startActivity(intent)
                }

                override fun onCodeAutoRetrievalTimeOut(verificationId: String) {
                    super.onCodeAutoRetrievalTimeOut(verificationId)
                    Log.d(TAG, "onCodeAutoRetrievalTimeOut: $verificationId")
                }
            }

            val options = PhoneAuthOptions.newBuilder(auth)
                .setPhoneNumber(phoneNumber)
                .setTimeout(60L, TimeUnit.SECONDS)
                .setActivity(this)
                .setCallbacks(callbacks)
                .build()

            PhoneAuthProvider.verifyPhoneNumber(options)
        }
    }

    private fun isValidPhone(phone: String): Boolean {
        return phone.startsWith("+")
                && phone.length in 11..15
                && phone.drop(1).all { it.isDigit() }
    }
}