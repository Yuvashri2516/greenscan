package com.greenscan.app.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.greenscan.app.data.GreenScanRepository
import com.greenscan.app.model.ChatMessage
import kotlinx.coroutines.launch

class ChatViewModel(private val repository: GreenScanRepository) : ViewModel() {

    private val _messages = MutableLiveData<List<ChatMessage>>(emptyList())
    val messages: LiveData<List<ChatMessage>> = _messages

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private var scanContext: Map<String, Any>? = null

    fun setScanContext(context: Map<String, Any>) {
        this.scanContext = context
    }

    fun sendMessage(userText: String) {
        if (userText.isBlank()) return

        val currentList = _messages.value.orEmpty().toMutableList()
        val userMsg = ChatMessage(text = userText, isUser = true)
        currentList.add(userMsg)
        _messages.value = currentList
        _isLoading.value = true

        viewModelScope.launch {
            val result = repository.sendChatMessage(userText, scanContext)
            _isLoading.value = false
            result.onSuccess { response ->
                val botMsg = ChatMessage(text = response.reply, isUser = false)
                val updatedList = _messages.value.orEmpty().toMutableList()
                updatedList.add(botMsg)
                _messages.value = updatedList
            }.onFailure {
                val errorMsg = ChatMessage(text = "Unable to connect to GreenScan AI assistant.", isUser = false)
                val updatedList = _messages.value.orEmpty().toMutableList()
                updatedList.add(errorMsg)
                _messages.value = updatedList
            }
        }
    }
}
