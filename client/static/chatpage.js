// === ConnectSphere Chat JavaScript - Fixed Alignment ===

// --- CONFIGURATION ---
const config = {
    backendHost: "localhost:5002", // backend API + WS host
    reconnectInterval: 5000, // 5 seconds
    maxReconnectAttempts: 5
};

// --- GLOBAL STATE ---
let ws = null;
let username = '';
let currentRoom = 'general';
let reconnectAttempts = 0;
let isConnecting = false;

// --- DOM ELEMENTS ---
const app = {
    // Main containers
    loginSection: document.getElementById('loginSection'),
    chatHeader: document.getElementById('chatHeader'),
    messageForm: document.getElementById('messageForm'),
    messages: document.getElementById('messages'),
    
    // Input elements
    messageInput: document.getElementById('messageInput'),
    newRoomInput: document.getElementById('newRoomInput'),
    
    // Display elements
    currentRoomName: document.getElementById('currentRoomName'),
    connectionStatus: document.getElementById('connectionStatus'),
    profileUsername: document.getElementById('profileUsername'),
    
    // Interactive elements
    userProfile: document.getElementById('userProfile'),
    logoutBtn: document.getElementById('logoutBtn'),
    createRoomBtn: document.getElementById('createRoomBtn'),
    roomList: document.getElementById('roomList'),
    
    // Error modal
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage')
};

// --- ERROR HANDLING ---
function showError(message) {
    console.error('Error:', message);
    if (app.errorModal && app.errorMessage) {
        app.errorMessage.textContent = message;
        app.errorModal.classList.add('show');
    } else {
        alert(message); // Fallback
    }
}

function closeErrorModal() {
    if (app.errorModal) {
        app.errorModal.classList.remove('show');
    }
}

// --- CONNECTION MANAGEMENT ---
function connect() {
    if (isConnecting) {
        console.log('Already attempting to connect...');
        return;
    }
    
    const token = sessionStorage.getItem("accessToken");
    if (!token) {
        showError("You must log in first!");
        return;
    }

    try {
        // Decode JWT payload to display username
        const payload = JSON.parse(atob(token.split(".")[1]));
        username = payload.user?.username || payload.username || "guest";
        
        isConnecting = true;
        updateConnectionStatus('connecting');

        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${config.backendHost}/ws/chat?room_id=${currentRoom}&token=${token}`;
        
        console.log(`🔌 Connecting to: ${wsUrl}`);
        ws = new WebSocket(wsUrl);
        setupWebSocketEventHandlers();
        
    } catch (error) {
        console.error('Failed to decode token or connect:', error);
        showError('Invalid authentication token. Please log in again.');
        isConnecting = false;
    }
}

function setupWebSocketEventHandlers() {
    if (!ws) return;

    ws.onopen = () => {
        console.log("✅ Connected to chat");
        isConnecting = false;
        reconnectAttempts = 0;
        
        showChatInterface();
        updateProfile();
        updateCurrentRoom(currentRoom);
        updateConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 Received message:', data);
            addMessageToUI(data);
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };

    ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
        isConnecting = false;
        updateConnectionStatus('disconnected');
        
        // Auto-reconnect if not a user-initiated close
        if (event.code !== 1000 && reconnectAttempts < config.maxReconnectAttempts) {
            scheduleReconnect();
        }
    };

    ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        isConnecting = false;
        updateConnectionStatus('error');
    };
}

function scheduleReconnect() {
    reconnectAttempts++;
    console.log(`🔄 Scheduling reconnect attempt ${reconnectAttempts}/${config.maxReconnectAttempts}`);
    
    setTimeout(() => {
        if (reconnectAttempts <= config.maxReconnectAttempts) {
            console.log(`🔄 Reconnect attempt ${reconnectAttempts}`);
            connect();
        } else {
            showError('Connection lost. Please refresh the page to reconnect.');
        }
    }, config.reconnectInterval);
}

function updateConnectionStatus(status) {
    if (!app.connectionStatus) return;
    
    const statusMap = {
        'connected': '<span class="online-indicator"></span>Connected',
        'connecting': '<span class="online-indicator" style="background: orange;"></span>Connecting...',
        'disconnected': '<span class="offline-indicator"></span>Disconnected',
        'error': '<span class="offline-indicator"></span>Connection Error'
    };
    
    app.connectionStatus.innerHTML = statusMap[status] || statusMap['disconnected'];
}

// --- MESSAGE HANDLING ---
function sendMessage() {
    const message = app.messageInput.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
        if (!message) return;
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            showError('Not connected to chat. Please wait for reconnection.');
        }
        return;
    }

    try {
        const messageData = {
            type: "message",
            message: message,
            room_id: currentRoom
        };
        
        ws.send(JSON.stringify(messageData));
        app.messageInput.value = "";
        console.log('📤 Message sent:', messageData);
        
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message. Please try again.');
    }
}

function addMessageToUI(data) {
    if (!app.messages) return;
    
    const messageDiv = document.createElement("div");
    const isOwnMessage = data.username === username;
    const isSystemMessage = isSystemMessageType(data.message_type);
    
    // Determine message class based on type and sender
    let messageClass = 'message';
    if (isSystemMessage) {
        messageClass += ' system-message';
    } else if (isOwnMessage) {
        messageClass += ' own-message';
    } else {
        messageClass += ' other-message';
    }
    
    messageDiv.className = messageClass;
    
    // Format timestamp
    const timestamp = data.timestamp ? new Date(data.timestamp) : new Date();
    const timeString = timestamp.toLocaleTimeString([], {
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // Create message content based on type
    if (isSystemMessage) {
        // System messages are simple and centered
        messageDiv.innerHTML = `<div class="message-content">${escapeHtml(data.message)}</div>`;
    } else {
        // Regular chat messages with header and content
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="username">${escapeHtml(data.username || 'Unknown')}</span>
                <span class="timestamp">${timeString}</span>
            </div>
            <div class="message-content">${escapeHtml(data.message || '')}</div>
        `;
    }
    
    // Add to messages container and scroll to bottom
    app.messages.appendChild(messageDiv);
    scrollToBottom();
    
    console.log(`💬 Added ${messageClass} message from ${data.username}`);
}

function isSystemMessageType(messageType) {
    const systemTypes = ['user_join', 'user_leave', 'system', 'room_update'];
    return systemTypes.includes(messageType);
}

function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function scrollToBottom() {
    if (app.messages) {
        app.messages.scrollTop = app.messages.scrollHeight;
    }
}

// --- UI STATE MANAGEMENT ---
function showChatInterface() {
    app.loginSection?.classList.add("hidden");
    app.chatHeader?.classList.remove("hidden");
    app.messageForm?.classList.remove("hidden");
    app.userProfile?.classList.remove("hidden");
}

function updateProfile() {
    if (app.profileUsername) {
        app.profileUsername.textContent = username;
    }
}

function updateCurrentRoom(roomId) {
    if (app.currentRoomName) {
        app.currentRoomName.textContent = `#${roomId}`;
    }
    // Update active room in sidebar
    updateActiveRoom(roomId);
}

function updateActiveRoom(roomId) {
    // Remove active class from all rooms
    const allRooms = app.roomList?.querySelectorAll('.room-item');
    allRooms?.forEach(room => room.classList.remove('active'));
    
    // Add active class to current room
    const activeRoom = app.roomList?.querySelector(`.room-item[data-room="${roomId}"]`);
    activeRoom?.classList.add('active');
}

// --- ROOM MANAGEMENT ---
function createOrJoinRoom() {
    const newRoomName = app.newRoomInput?.value.trim();
    if (!newRoomName || newRoomName.length === 0) {
        showError('Please enter a room name');
        return;
    }
    
    if (newRoomName.length > 20) {
        showError('Room name must be 20 characters or less');
        return;
    }
    
    // Sanitize room name
    const sanitizedRoomName = newRoomName.replace(/[^a-zA-Z0-9_-]/g, '').toLowerCase();
    if (sanitizedRoomName !== newRoomName.toLowerCase()) {
        showError('Room name can only contain letters, numbers, hyphens, and underscores');
        return;
    }
    
    if (sanitizedRoomName === currentRoom) {
        showError('You are already in this room');
        return;
    }
    
    switchRoom(sanitizedRoomName);
    app.newRoomInput.value = "";
}

function switchRoom(roomId) {
    if (roomId === currentRoom) {
        console.log(`Already in room ${roomId}`);
        return;
    }
    
    console.log(`🔄 Switching from ${currentRoom} to ${roomId}`);
    currentRoom = roomId;
    
    // Close existing connection and reconnect to new room
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Switching rooms");
    }
    
    // Clear messages for new room
    clearMessages();
    
    // Connect to new room
    connect();
    
    // Add room to sidebar if it doesn't exist
    addRoomToSidebar(roomId);
    
    // Update UI
    updateCurrentRoom(roomId);
}

function addRoomToSidebar(roomId) {
    if (!app.roomList) return;
    
    // Check if room already exists
    const existingRoom = app.roomList.querySelector(`.room-item[data-room="${roomId}"]`);
    if (existingRoom) return;
    
    const li = document.createElement("li");
    li.className = "room-item";
    li.setAttribute('data-room', roomId);
    li.innerHTML = `
        <div class="room-info">
            <div class="room-name">#${roomId}</div>
            <div class="room-users">Click to join</div>
        </div>
    `;
    
    li.addEventListener("click", () => switchRoom(roomId));
    app.roomList.appendChild(li);
    
    console.log(`➕ Added room ${roomId} to sidebar`);
}

function clearMessages() {
    if (app.messages) {
        // Keep welcome message, remove others
        const welcomeMsg = app.messages.querySelector('.welcome-message');
        app.messages.innerHTML = '';
        if (welcomeMsg) {
            app.messages.appendChild(welcomeMsg);
        }
    }
}

// --- LOGOUT FUNCTIONALITY ---
async function logout() {
    if (!app.logoutBtn) return;
    
    // Disable button to prevent multiple clicks
    app.logoutBtn.disabled = true;
    app.logoutBtn.textContent = 'Logging out...';

    try {
        const refreshToken = sessionStorage.getItem('refreshToken') || 
                            localStorage.getItem('refreshToken');
        
        if (refreshToken) {
            const response = await fetch('http://127.0.0.1:8000/api/v1/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const result = await response.json();
            console.log('✅ Server logout successful:', result.message);
        } else {
            console.warn('⚠️ No refresh token found, performing client-side logout only');
        }
        
    } catch (error) {
        console.warn('⚠️ Logout API call failed, continuing with client cleanup:', error);
    } finally {
        // Perform cleanup regardless of API success
        if (ws) {
            ws.close(1000, 'User logout');
            ws = null;
        }
        
        // Clear authentication data
        const tokensToRemove = [
            'accessToken', 'refreshToken', 'user_data', 
            'auth_token', 'session_id'
        ];
        
        tokensToRemove.forEach(token => {
            sessionStorage.removeItem(token);
            localStorage.removeItem(token);
        });
        
        // Clear cookies if used
        document.cookie.split(';').forEach(cookie => {
            const name = cookie.split('=')[0].trim();
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        });
        
        console.log('🔐 Logout cleanup completed');
        
        // Redirect to login page
        window.location.replace('/');
    }
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    // Message input - send on Enter
    app.messageInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Room creation - create on Enter
    app.newRoomInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            createOrJoinRoom();
        }
    });
    
    // Create room button
    app.createRoomBtn?.addEventListener('click', createOrJoinRoom);
    
    // Logout button
    app.logoutBtn?.addEventListener('click', logout);
    
    // Error modal close on click outside
    app.errorModal?.addEventListener('click', (e) => {
        if (e.target === app.errorModal) {
            closeErrorModal();
        }
    });
    
    // Prevent form submissions
    app.messageForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });
}

// --- INITIALIZATION ---
function initializeChat() {
    console.log('🚀 Initializing ConnectSphere Chat...');
    
    // Set up event listeners
    setupEventListeners();
    
    // Add default room to sidebar
    addRoomToSidebar('general');
    updateActiveRoom('general');
    
    // Check if user is already logged in
    const token = sessionStorage.getItem("accessToken");
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            const expiry = payload.exp * 1000; // Convert to milliseconds
            
            if (Date.now() < expiry) {
                console.log('👤 Found valid token, auto-connecting...');
                // Small delay to ensure DOM is ready
                setTimeout(connect, 100);
            } else {
                console.log('⏰ Token expired, please log in again');
                sessionStorage.removeItem("accessToken");
            }
        } catch (error) {
            console.error('❌ Invalid token format:', error);
            sessionStorage.removeItem("accessToken");
        }
    } else {
        console.log('🔐 No authentication token found');
    }
    
    console.log('✅ Chat initialization complete');
}

// --- GLOBAL FUNCTIONS (for HTML onclick handlers) ---
window.connect = connect;
window.sendMessage = sendMessage;
window.closeErrorModal = closeErrorModal;

// --- START APPLICATION ---
document.addEventListener('DOMContentLoaded', initializeChat);