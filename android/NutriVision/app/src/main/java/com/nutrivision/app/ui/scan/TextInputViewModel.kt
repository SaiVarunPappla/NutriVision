package com.nutrivision.app.ui.scan

import androidx.lifecycle.*
import com.nutrivision.app.data.model.*
import com.nutrivision.app.data.network.RetrofitClient
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

class TextInputViewModel : ViewModel() {

    private val _analysisResult = MutableLiveData<AnalysisResult>()
    val analysisResult: LiveData<AnalysisResult> = _analysisResult

    fun analyzeIngredients(ingredients: String, userId: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.apiService.scanText(TextScanRequest(ingredients, userId))
                if (response.isSuccessful) {
                    val scanResponse = response.body()
                    _analysisResult.postValue(AnalysisResult(scanResponse = scanResponse, errorMessage = null, statusMessage = scanResponse?.status_message))
                } else {
                    val errorBody = response.errorBody()?.string()
                    val errorMessage = "Backend Error: ${response.code()} ${response.message()} ${errorBody ?: ""}".trim()
                    _analysisResult.postValue(AnalysisResult(scanResponse = null, errorMessage = errorMessage, statusMessage = "Error during analysis."))
                }
            } catch (e: HttpException) {
                _analysisResult.postValue(AnalysisResult(scanResponse = null, errorMessage = "HTTP Error: ${e.message()}", statusMessage = "Network error."))
            } catch (e: IOException) {
                _analysisResult.postValue(AnalysisResult(scanResponse = null, errorMessage = "Connection Error: ${e.message ?: "Network unreachable"}", statusMessage = "Network error."))
            } catch (e: Exception) {
                _analysisResult.postValue(AnalysisResult(scanResponse = null, errorMessage = "An unexpected error occurred: ${e.message ?: "Unknown error"}", statusMessage = "Analysis failed."))
            }
        }
    }
}

