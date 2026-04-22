package com.nutrivision.app.ui.ai.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.nutrivision.app.data.model.ScanResponse

class SharedScanResultViewModel : ViewModel() {

    private val _scanResponse = MutableLiveData<ScanResponse?>()
    val scanResponse: LiveData<ScanResponse?> = _scanResponse

    fun setScanResponse(response: ScanResponse?) {
        _scanResponse.value = response
    }
}