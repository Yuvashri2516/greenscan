package com.greenscan.app.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.greenscan.app.data.GreenScanRepository
import com.greenscan.app.model.PredictionResponse
import kotlinx.coroutines.launch
import java.io.File

sealed class ScanUiState {
    object Idle : ScanUiState()
    object Loading : ScanUiState()
    data class Success(val response: PredictionResponse) : ScanUiState()
    data class Error(val message: String) : ScanUiState()
}

class ScanViewModel(private val repository: GreenScanRepository) : ViewModel() {

    private val _uiState = MutableLiveData<ScanUiState>(ScanUiState.Idle)
    val uiState: LiveData<ScanUiState> = _uiState

    fun analyzeLeafImage(imageFile: File) {
        _uiState.value = ScanUiState.Loading
        viewModelScope.launch {
            val result = repository.predictLeafDisease(imageFile)
            result.onSuccess { response ->
                _uiState.value = ScanUiState.Success(response)
            }.onFailure { exception ->
                _uiState.value = ScanUiState.Error(exception.message ?: "Failed to connect to GreenScan server.")
            }
        }
    }
}
