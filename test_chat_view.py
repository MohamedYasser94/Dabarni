# Simple test view to test chat without authentication
from django.shortcuts import render
from django.http import HttpResponse
import json

def test_chat_view(request, dialog_id):
    """Test chat view without authentication"""
    dialog_id_str = str(dialog_id)
    
    template_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Test</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chat-container { max-width: 600px; margin: 0 auto; }
        .message-list { height: 300px; border: 1px solid #ccc; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .message { margin: 10px 0; padding: 8px; background: #f0f0f0; border-radius: 4px; }
        .message.own { background: #007bff; color: white; text-align: right; }
        .chat-input { width: 70%; padding: 8px; }
        .send-btn { padding: 8px 15px; background: #007bff; color: white; border: none; cursor: pointer; }
        .error { color: red; font-weight: bold; }
        .status { color: green; font-size: 12px; }
    </style>
</head>
<body>
    <div class="chat-container" id="chat-app">
        <h2>Chat Test - Dialog: ''' + dialog_id_str + '''</h2>
        <div class="status">Connection Status: {{ connectionStatus }}</div>
        <div class="error" v-if="errorMessage">{{ errorMessage }}</div>
        
        <div class="message-list" id="message-list">
            <div v-for="message in messages" :key="message.random_id" :class="['message', {'own': message.sender == currentUserPk}]">
                <strong>{{ message.sender == currentUserPk ? 'You' : 'Other' }}:</strong> {{ message.text }}
                <small>({{ message.created_at }})</small>
            </div>
        </div>
        
        <div>
            <input type="text" v-model="newMessage" @keyup.enter="sendMessage" class="chat-input" placeholder="Type a message...">
            <button @click="sendMessage" class="send-btn">Send</button>
        </div>
    </div>

    <script>
    const { createApp } = Vue;
    
    const ChatApp = createApp({
        data() {
            return {
                dialogId: "''' + dialog_id_str + '''",
                currentUserPk: 3, // Provider user ID
                messages: [],
                newMessage: '',
                chatSocket: null,
                errorMessage: '',
                connectionStatus: 'Disconnected'
            };
        },
        methods: {
            initWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
                const url = `${protocol}${window.location.host}/ws/chat/${this.dialogId}/`;
                
                console.log('Connecting to WebSocket:', url);
                this.chatSocket = new WebSocket(url);

                this.chatSocket.onopen = () => {
                    console.log('WebSocket connection established');
                    this.connectionStatus = 'Connected';
                    this.errorMessage = '';
                };

                this.chatSocket.onclose = (event) => {
                    console.log('WebSocket closed:', event);
                    this.connectionStatus = 'Disconnected';
                    this.errorMessage = 'Connection closed';
                };

                this.chatSocket.onmessage = (e) => {
                    try {
                        const data = JSON.parse(e.data);
                        console.log('WebSocket message received:', data);
                        
                        if (data.msg_type === 3) { // TextMessage
                            this.appendNewMessage(data);
                        } else if (data.msg_type === 4) { // MessageIdCreated
                            const message = this.messages.find(m => m.random_id === data.random_id);
                            if (message) {
                                message.db_id = data.db_id;
                            }
                        }
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                        this.errorMessage = 'Error receiving message: ' + error.message;
                    }
                };

                this.chatSocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.errorMessage = 'Connection error';
                    this.connectionStatus = 'Error';
                };
            },
            
            appendNewMessage(data) {
                const messageTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                const newMessage = {
                    random_id: data.random_id,
                    text: data.text,
                    sender: parseInt(data.sender),
                    sender_username: data.sender_username,
                    created_at: messageTime,
                };
                
                this.messages.push(newMessage);
                console.log('Message added:', newMessage);
                
                this.$nextTick(() => {
                    const messageList = document.getElementById('message-list');
                    if (messageList) {
                        messageList.scrollTop = messageList.scrollHeight;
                    }
                });
            },
            
            sendMessage() {
                if (!this.newMessage.trim()) {
                    this.errorMessage = 'Please enter a message';
                    setTimeout(() => { this.errorMessage = ''; }, 3000);
                    return;
                }
                
                if (!this.chatSocket || this.chatSocket.readyState !== WebSocket.OPEN) {
                    this.errorMessage = 'Not connected to chat';
                    setTimeout(() => { this.errorMessage = ''; }, 3000);
                    return;
                }

                const randomId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
                const messageData = {
                    msg_type: 3, // TextMessage
                    text: this.newMessage,
                    random_id: randomId,
                };
                
                console.log('Sending message:', messageData);
                
                try {
                    this.chatSocket.send(JSON.stringify(messageData));
                    this.newMessage = '';
                } catch (error) {
                    console.error('Error sending message:', error);
                    this.errorMessage = 'Failed to send message: ' + error.message;
                }
            }
        },
        
        mounted() {
            console.log('Chat app mounted');
            this.initWebSocket();
        },
        
        beforeUnmount() {
            if (this.chatSocket) {
                this.chatSocket.close();
            }
        }
    });

    ChatApp.mount('#chat-app');
    </script>
</body>
</html>
    '''
    
    return HttpResponse(template_content)
