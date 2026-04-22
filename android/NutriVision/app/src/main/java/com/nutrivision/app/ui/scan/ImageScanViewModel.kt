package com.nutrivision.app.ui.scan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutrivision.app.data.model.ScanResponse
import com.nutrivision.app.data.model.TextScanRequest
import com.nutrivision.app.data.network.RetrofitClient
import kotlinx.coroutines.launch

class ImageScanViewModel : ViewModel() {

    private val _scanResponse = MutableLiveData<ScanResponse?>()
    val scanResponse: LiveData<ScanResponse?> = _scanResponse

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage

    fun uploadRecognizedText(text: String, userId: String, productName: String?) {
        _isLoading.value = true

        viewModelScope.launch {
            try {
                val request = TextScanRequest(
                    text = text,
                    user_id = userId,
                    product_name = productName
                )

                val response = RetrofitClient.apiService.scanText(request)

                if (response.isSuccessful && response.body() != null) {
                    _scanResponse.value = response.body()
                    _errorMessage.value = null
                } else {
                    val errorBody = response.errorBody()?.string()
                    _errorMessage.value = "Scan failed: ${response.code()} - ${errorBody ?: "Unknown error"}"
                    _scanResponse.value = null
                }
            } catch (e: Exception) {
                _errorMessage.value = "An error occurred: ${e.message ?: "Unknown error"}"
                _scanResponse.value = null
            } finally {
                _isLoading.value = false
            }
        }
    }
}