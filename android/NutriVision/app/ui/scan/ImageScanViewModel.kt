package com.nutrivision.app.ui.scan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.data.network.RetrofitClient
import kotlinx.coroutines.launch
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class ImageScanViewModel : ViewModel() {
    private val _scanResponse = MutableLiveData<ScanResponse?>()
    val scanResponse: LiveData<ScanResponse?> = _scanResponse

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    fun uploadImage(imagePart: MultipartBody.Part, userId: String) {
        viewModelScope.launch {
            try {
                val userRequestBody = userId.toRequestBody(okhttp3.MultipartBody.FORM)
                val response = RetrofitClient.apiService.scanImage(imagePart, userRequestBody)

                if (response.isSuccessful) {
                    _scanResponse.value = response.body()
                } else {
                    _errorMessage.value = "Server error: ${response.code()}"
                }
            } catch (e: Exception) {
                _errorMessage.value = e.message
            }
        }
    }
}