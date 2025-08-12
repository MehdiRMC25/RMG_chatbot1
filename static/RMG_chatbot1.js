document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('chatbot-container');
  const header = document.getElementById('chatbot-header');
  const body = document.getElementById('chatbot-body');
  const input = document.getElementById('chatbot-input');

  header.addEventListener('click', () => container.classList.toggle('min'));

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      const msg = document.createElement('div');
      msg.className = 'chatbot-msg user';
      msg.textContent = input.value.trim();
      body.appendChild(msg);
      body.scrollTop = body.scrollHeight;
      input.value = '';
      // TODO: send to your backend here
    }
  });
});
