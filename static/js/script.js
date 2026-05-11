/* ============================================
   AI Data Analyst Agent - JavaScript
   File: static/js/script.js
   ============================================ */

// Copy to Clipboard Function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('✅ Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('❌ Failed to copy');
    });
}

// Show Toast Notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// Auto Scroll Chat to Bottom
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Add Animation to New Messages
function animateMessage(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        element.style.transition = 'all 0.3s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 100);
}

// Initialize on Page Load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 AI Data Analyst Agent - JavaScript Loaded');
    scrollToBottom();
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .toast-notification {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
    }
`;
document.head.appendChild(style);