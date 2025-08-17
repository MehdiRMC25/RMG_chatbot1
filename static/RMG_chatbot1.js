document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('chatbot-container');
  const header = document.getElementById('chatbot-header');
  const body = document.getElementById('chatbot-body');
  const input = document.getElementById('chatbot-input');

  // Toggle minimize/maximize when header clicked
  header.addEventListener('click', () => container.classList.toggle('min'));

  // Handle Enter key press
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      // Add user message
      const msg = document.createElement('div');
      msg.className = 'chatbot-msg user';
      msg.textContent = input.value.trim();
      body.appendChild(msg);
      body.scrollTop = body.scrollHeight;

      // Grab and clear input
      const userText = input.value.trim();
      input.value = '';

      // ✅ Show typing indicator right after user sends
      showTyping();

      // ✅ Send to your backend
      fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      })
      .then(res => res.json())
      .then(data => {
        // ✅ Hide typing indicator when reply arrives
        hideTyping();

        // Add bot reply
        const botMsg = document.createElement('div');
        botMsg.className = 'chatbot-msg bot';
        botMsg.textContent = data.reply;
        body.appendChild(botMsg);
        body.scrollTop = body.scrollHeight;
      })
      .catch(err => {
        hideTyping();
        console.error('Chat error:', err);
      });
    }
  });
});

// --- Typing indicator helpers ---
function showTyping() {
  const indicator = document.getElementById("typing-indicator");
  if (indicator) indicator.style.display = "flex";
}

function hideTyping() {
  const indicator = document.getElementById("typing-indicator");
  if (indicator) indicator.style.display = "none";
}
