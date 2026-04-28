const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

let sessionId = 'session_' + Math.random().toString(36).substring(2, 10);

function parseMarkdown(text) {
    // Basic Markdown Parser (Bold)
    let parsed = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Images: ![alt](url)
    parsed = parsed.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; border-radius: 8px; margin-top: 10px; margin-bottom: 10px; display: block;">');

    // Lists processing
    parsed = parsed.replace(/^\s*-\s+(.*)$/gm, '<li>$1</li>');
    if (parsed.includes('<li>')) {
        parsed = parsed.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    }

    return parsed;
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const formattedText = parseMarkdown(text);

    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <div class="avatar-img-small">🤖</div>
            <div class="msg-content">${formattedText}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="msg-content">${formattedText}</div>
        `;
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'bot');
    messageDiv.id = 'typing-indicator';

    messageDiv.innerHTML = `
        <div class="avatar-img-small">🤖</div>
        <div class="msg-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // UI Updates
    addMessage(text, 'user');
    userInput.value = '';
    userInput.focus();

    // Show typing animation
    addTypingIndicator();

    try {
        // Gửi fetch API tới cổng uvicorn FastAPI backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                thread_id: sessionId
            })
        });

        const data = await response.json();
        removeTypingIndicator();

        if (data.status === 'success') {
            addMessage(data.reply, 'bot');
        } else {
            addMessage(`Đã xảy ra sự cố: ${data.reply}`, 'bot');
        }

    } catch (err) {
        removeTypingIndicator();
        addMessage(`Vui lòng kiểm tra lại kết nối mạng. (Chi tiết lỗi gốc JS: ${err.message || err} | stack: ${err.stack})`, 'bot');
        console.error("Fetch Error:", err);
    }
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSend();
    }
});

// Auto focus on load
window.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
});

function sendSuggestion(text) {
    // Fill input and send
    userInput.value = text;
    handleSend();
}

// Header Actions Logic
const clearChatBtn = document.getElementById('clear-chat');
if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
        // Reset chat box content
        chatBox.innerHTML = `
            <div class="message bot">
                <div class="avatar-img-small">🤖</div>
                <div class="msg-content">Kính chào quý khách! Tôi là trợ lý ảo. Tôi có thể giúp gì cho quý khách về thực đơn hay đặt bàn hôm nay ạ?</div>
            </div>
            
            <div class="suggestions" id="suggestions">
                <div class="suggestion-chip" onclick="sendSuggestion('Nhà hàng có bao nhiêu chi nhánh?')">Nhà hàng có bao nhiêu chi nhánh?</div>
                <div class="suggestion-chip" onclick="sendSuggestion('Menu của nhà hàng')">Menu của nhà hàng</div>
            </div>
        `;
        // Generate new session to clear backend LLM context
        sessionId = 'session_' + Math.random().toString(36).substring(2, 10);
    });
}

const themeToggleBtn = document.getElementById('theme-toggle');
if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        if (document.body.classList.contains('light-mode')) {
            themeToggleBtn.innerHTML = '🌙';
            themeToggleBtn.title = "Chuyển đổi giao diện Tối/Sáng";
        } else {
            themeToggleBtn.innerHTML = '☀️';
            themeToggleBtn.title = "Chuyển đổi giao diện Sáng/Tối";
        }
    });
}
