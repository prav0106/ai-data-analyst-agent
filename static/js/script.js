/* ============================================
   AI Data Analyst Agent — Studio UI helpers
   (Optional enhancements; the app works fully
   without JS. Used for copy/toast niceties.)
   ============================================ */

// Copy text to clipboard with a toast
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard');
    }).catch(() => {
        showToast('Could not copy');
    });
}

// Toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2200);
}

// Smooth-scroll the chat area to the latest message
function scrollChatToBottom() {
    const chats = document.querySelectorAll('[data-testid="stChatMessage"]');
    if (chats.length) {
        chats[chats.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
}
