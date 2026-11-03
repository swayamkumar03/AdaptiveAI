/**
 * AdaptiveAI Embeddable Website Chatbot Widget (widget.js)
 * High-performance, zero-dependency, self-contained embeddable widget.
 *
 * Usage on any website:
 * <script src="http://localhost:5173/widget.js" data-chatbot-id="adaptiveai-demo"></script>
 */

(function () {
  'use strict';

  // Prevent multiple initializations on the same page
  if (window.__AdaptiveAIWidgetLoaded) return;
  window.__AdaptiveAIWidgetLoaded = true;

  // 1. Locate current script element and extract configuration
  const currentScript =
    document.currentScript ||
    document.querySelector('script[data-chatbot-id]') ||
    document.querySelector('script[src*="widget.js"]');

  const chatbotId =
    (currentScript && currentScript.getAttribute('data-chatbot-id')) ||
    'adaptiveai-demo';

  const apiBase =
    (currentScript && currentScript.getAttribute('data-api-base')) ||
    'http://127.0.0.1:8000/api/v1';

  // State management
  let isOpen = false;
  let config = {
    company_name: 'AdaptiveAI Demo',
    company_slug: chatbotId,
    bot_name: 'AI Support Assistant',
    brand_description: 'Continuous Knowledge AI',
    welcome_message: 'Hello! How can I help you today?',
  };
  let sessionId = sessionStorage.getItem(`adaptiveai_session_${chatbotId}`) || null;
  let messages = [];
  let isSending = false;

  // 2. Inject CSS Styles
  const styles = `
    #adaptiveai-widget-root {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      box-sizing: border-box;
    }
    #adaptiveai-widget-root * {
      box-sizing: border-box;
    }

    /* Floating Launcher Button */
    .aai-launcher {
      display: flex;
      align-items: center;
      gap: 10px;
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #ffffff;
      border: none;
      border-radius: 9999px;
      padding: 12px 18px 12px 16px;
      box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.45), 0 8px 10px -6px rgba(37, 99, 235, 0.3);
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .aai-launcher:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 14px 28px -5px rgba(37, 99, 235, 0.55);
    }
    .aai-launcher-icon {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .aai-launcher-text {
      font-size: 14px;
      font-weight: 600;
      letter-spacing: -0.01em;
    }

    /* Chat Window Container */
    .aai-panel {
      position: absolute;
      bottom: 70px;
      right: 0;
      width: 380px;
      max-width: calc(100vw - 32px);
      height: 580px;
      max-height: calc(100vh - 100px);
      background: #0f172a;
      border: 1px solid rgba(51, 65, 85, 0.8);
      border-radius: 20px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.05);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(16px) scale(0.96);
      pointer-events: none;
      transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .aai-panel.aai-open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }

    /* Header */
    .aai-header {
      background: #1e293b;
      border-bottom: 1px solid rgba(51, 65, 85, 0.8);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .aai-header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .aai-avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .aai-status-dot {
      position: absolute;
      bottom: -2px;
      right: -2px;
      width: 10px;
      height: 10px;
      background: #10b981;
      border: 2px solid #1e293b;
      border-radius: 50%;
    }
    .aai-title {
      color: #f8fafc;
      font-size: 14px;
      font-weight: 600;
      margin: 0;
    }
    .aai-subtitle {
      color: #94a3b8;
      font-size: 11px;
      margin: 0;
    }
    .aai-close-btn {
      background: transparent;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      padding: 6px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s, color 0.15s;
    }
    .aai-close-btn:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
    }

    /* Message list */
    .aai-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background: #090d16;
    }
    .aai-body::-webkit-scrollbar {
      width: 5px;
    }
    .aai-body::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 4px;
    }

    /* Message bubbles */
    .aai-msg {
      display: flex;
      flex-direction: column;
      max-width: 86%;
      animation: aaiFadeIn 0.2s ease-out;
    }
    @keyframes aaiFadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .aai-msg-user {
      align-self: flex-end;
    }
    .aai-msg-user .aai-bubble {
      background: #2563eb;
      color: #ffffff;
      border-radius: 16px 16px 4px 16px;
    }
    .aai-msg-bot {
      align-self: flex-start;
    }
    .aai-msg-bot .aai-bubble {
      background: #1e293b;
      color: #e2e8f0;
      border: 1px solid rgba(51, 65, 85, 0.6);
      border-radius: 16px 16px 16px 4px;
    }
    .aai-bubble {
      padding: 10px 14px;
      font-size: 13px;
      line-height: 1.5;
      word-break: break-word;
    }

    /* Sources and Escalation */
    .aai-sources {
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 11px;
      color: #94a3b8;
    }
    .aai-source-badge {
      display: inline-block;
      background: rgba(37, 99, 235, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(37, 99, 235, 0.3);
      padding: 2px 6px;
      border-radius: 4px;
      margin-right: 4px;
      margin-top: 4px;
      font-size: 10px;
    }
    .aai-escalation-alert {
      margin-top: 8px;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: #fbbf24;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 11px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* Feedback */
    .aai-feedback {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 4px;
      font-size: 11px;
      color: #64748b;
    }
    .aai-fb-btn {
      background: transparent;
      border: none;
      color: #64748b;
      cursor: pointer;
      padding: 2px 4px;
      border-radius: 4px;
      transition: color 0.15s, background 0.15s;
    }
    .aai-fb-btn:hover {
      color: #cbd5e1;
      background: rgba(255, 255, 255, 0.06);
    }
    .aai-fb-btn.active {
      color: #3b82f6;
    }

    /* Typing indicator */
    .aai-typing {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 8px 12px;
      background: #1e293b;
      border-radius: 14px;
      width: fit-content;
    }
    .aai-dot {
      width: 6px;
      height: 6px;
      background: #94a3b8;
      border-radius: 50%;
      animation: aaiPulse 1.4s infinite ease-in-out;
    }
    .aai-dot:nth-child(2) { animation-delay: 0.2s; }
    .aai-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes aaiPulse {
      0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
      40% { transform: scale(1); opacity: 1; }
    }

    /* Footer Input */
    .aai-footer {
      background: #1e293b;
      border-top: 1px solid rgba(51, 65, 85, 0.8);
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .aai-input-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .aai-input {
      flex: 1;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 9px 12px;
      color: #ffffff;
      font-size: 13px;
      outline: none;
      transition: border-color 0.15s;
    }
    .aai-input:focus {
      border-color: #3b82f6;
    }
    .aai-send-btn {
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 10px;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: background 0.15s;
      flex-shrink: 0;
    }
    .aai-send-btn:hover:not(:disabled) {
      background: #1d4ed8;
    }
    .aai-send-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .aai-branding {
      text-align: center;
      font-size: 10px;
      color: #64748b;
      margin: 0;
    }
    .aai-branding a {
      color: #94a3b8;
      text-decoration: none;
      font-weight: 500;
    }
  `;

  // 3. Create DOM Elements
  const container = document.createElement('div');
  container.id = 'adaptiveai-widget-root';

  const styleEl = document.createElement('style');
  styleEl.textContent = styles;
  document.head.appendChild(styleEl);

  container.innerHTML = `
    <!-- Floating Launcher -->
    <button class="aai-launcher" id="aai-launcher" aria-label="Open support chat">
      <div class="aai-launcher-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <span class="aai-launcher-text">Chat with AI</span>
    </button>

    <!-- Chat Panel -->
    <div class="aai-panel" id="aai-panel">
      <!-- Header -->
      <div class="aai-header">
        <div class="aai-header-left">
          <div class="aai-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 8V4H8"></path>
              <rect width="16" height="12" x="4" y="8" rx="2"></rect>
              <path d="M2 14h2"></path>
              <path d="M20 14h2"></path>
              <path d="M15 13v2"></path>
              <path d="M9 13v2"></path>
            </svg>
            <div class="aai-status-dot"></div>
          </div>
          <div>
            <h4 class="aai-title" id="aai-bot-name">Support Assistant</h4>
            <p class="aai-subtitle" id="aai-company-name">AdaptiveAI</p>
          </div>
        </div>
        <button class="aai-close-btn" id="aai-close-btn" title="Close chat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Messages Body -->
      <div class="aai-body" id="aai-body">
        <!-- Messages will render dynamically here -->
      </div>

      <!-- Footer Input -->
      <div class="aai-footer">
        <div class="aai-input-row">
          <input
            type="text"
            class="aai-input"
            id="aai-input"
            placeholder="Type your question..."
            autocomplete="off"
          />
          <button class="aai-send-btn" id="aai-send-btn" title="Send message">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
        <p class="aai-branding">
          Powered by <a href="#" target="_blank" rel="noopener">AdaptiveAI</a>
        </p>
      </div>
    </div>
  `;

  document.body.appendChild(container);

  // 4. Element references
  const launcherBtn = document.getElementById('aai-launcher');
  const panel = document.getElementById('aai-panel');
  const closeBtn = document.getElementById('aai-close-btn');
  const messagesBody = document.getElementById('aai-body');
  const inputField = document.getElementById('aai-input');
  const sendBtn = document.getElementById('aai-send-btn');
  const botNameEl = document.getElementById('aai-bot-name');
  const companyNameEl = document.getElementById('aai-company-name');

  // Toggle open/close
  function toggleWidget(open) {
    isOpen = typeof open === 'boolean' ? open : !isOpen;
    if (isOpen) {
      panel.classList.add('aai-open');
      inputField.focus();
    } else {
      panel.classList.remove('aai-open');
    }
  }

  launcherBtn.addEventListener('click', () => toggleWidget(true));
  closeBtn.addEventListener('click', () => toggleWidget(false));

  // Render message list
  function renderMessages() {
    messagesBody.innerHTML = '';

    messages.forEach((msg, idx) => {
      const msgDiv = document.createElement('div');
      msgDiv.className = `aai-msg ${msg.role === 'user' ? 'aai-msg-user' : 'aai-msg-bot'}`;

      let sourcesHtml = '';
      if (msg.sources && msg.sources.length > 0) {
        sourcesHtml = `
          <div class="aai-sources">
            <strong>Sources:</strong><br/>
            ${msg.sources
              .slice(0, 3)
              .map(
                (s) =>
                  `<span class="aai-source-badge">${
                    s.title || s.source_title || (s.type === 'verified_experience' ? 'Verified Experience' : 'Knowledge Base')
                  }</span>`
              )
              .join('')}
          </div>
        `;
      }

      let escalationHtml = '';
      if (msg.is_escalated) {
        escalationHtml = `
          <div class="aai-escalation-alert">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <span>Referred to human support representative.</span>
          </div>
        `;
      }

      let feedbackHtml = '';
      if (msg.role === 'assistant' && msg.id) {
        feedbackHtml = `
          <div class="aai-feedback">
            <span>Was this helpful?</span>
            <button class="aai-fb-btn ${msg.feedback === 'POSITIVE' ? 'active' : ''}" data-idx="${idx}" data-val="POSITIVE" title="Helpful">👍</button>
            <button class="aai-fb-btn ${msg.feedback === 'NEGATIVE' ? 'active' : ''}" data-idx="${idx}" data-val="NEGATIVE" title="Not helpful">👎</button>
          </div>
        `;
      }

      msgDiv.innerHTML = `
        <div class="aai-bubble">${escapeHtml(msg.text)}</div>
        ${sourcesHtml}
        ${escalationHtml}
        ${feedbackHtml}
      `;

      messagesBody.appendChild(msgDiv);
    });

    // Scroll to bottom
    messagesBody.scrollTop = messagesBody.scrollHeight;

    // Attach feedback handlers
    document.querySelectorAll('.aai-fb-btn').forEach((btn) => {
      btn.addEventListener('click', handleFeedbackClick);
    });
  }

  // Handle feedback clicks
  async function handleFeedbackClick(e) {
    const btn = e.currentTarget;
    const idx = parseInt(btn.getAttribute('data-idx'), 10);
    const val = btn.getAttribute('data-val');
    const msg = messages[idx];
    if (!msg || !msg.id || msg.feedback) return;

    msg.feedback = val;
    renderMessages();

    try {
      await fetch(`${apiBase}/widget/${encodeURIComponent(chatbotId)}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: msg.id,
          rating: val,
        }),
      });
    } catch (err) {
      console.warn('[AdaptiveAI Widget] Feedback failed:', err);
    }
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/\n/g, '<br/>');
  }

  // Show typing indicator
  function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.id = 'aai-typing-indicator';
    typingDiv.className = 'aai-typing';
    typingDiv.innerHTML = `
      <div class="aai-dot"></div>
      <div class="aai-dot"></div>
      <div class="aai-dot"></div>
    `;
    messagesBody.appendChild(typingDiv);
    messagesBody.scrollTop = messagesBody.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('aai-typing-indicator');
    if (indicator) indicator.remove();
  }

  // Send message
  async function sendMessage() {
    const text = inputField.value.trim();
    if (!text || isSending) return;

    inputField.value = '';
    isSending = true;
    sendBtn.disabled = true;

    // Add user message
    messages.push({ role: 'user', text: text });
    renderMessages();
    showTypingIndicator();

    try {
      const response = await fetch(
        `${apiBase}/widget/${encodeURIComponent(chatbotId)}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            session_id: sessionId,
          }),
        }
      );

      removeTypingIndicator();

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.session_id) {
        sessionId = data.session_id;
        sessionStorage.setItem(`adaptiveai_session_${chatbotId}`, sessionId);
      }

      messages.push({
        id: data.assistant_message_id,
        role: 'assistant',
        text: data.answer || 'Thank you for your question.',
        sources: data.sources || [],
        confidence_score: data.confidence_score,
        is_escalated: data.is_escalated,
      });

      renderMessages();
    } catch (err) {
      removeTypingIndicator();
      console.error('[AdaptiveAI Widget Error]', err);
      messages.push({
        role: 'assistant',
        text: 'Sorry, I encountered an issue connecting to the knowledge service. Please try again.',
      });
      renderMessages();
    } finally {
      isSending = false;
      sendBtn.disabled = false;
      inputField.focus();
    }
  }

  // Handle Enter key
  inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendBtn.addEventListener('click', sendMessage);

  // 5. Initialize config from server
  async function initConfig() {
    try {
      const res = await fetch(`${apiBase}/widget/${encodeURIComponent(chatbotId)}/config`);
      if (res.ok) {
        const data = await res.json();
        config = data;
        botNameEl.textContent = config.bot_name || 'Support Assistant';
        companyNameEl.textContent = config.company_name || 'AdaptiveAI';

        // Add welcome message if chat history is empty
        if (messages.length === 0) {
          messages.push({
            role: 'assistant',
            text: config.welcome_message || `Hello! How can I assist you with ${config.company_name} today?`,
          });
          renderMessages();
        }
      }
    } catch (err) {
      console.warn('[AdaptiveAI Widget] Failed to load config:', err);
      if (messages.length === 0) {
        messages.push({
          role: 'assistant',
          text: 'Hello! How can I assist you today?',
        });
        renderMessages();
      }
    }
  }

  initConfig();

  // Expose global controller if website wants programmatic trigger
  window.AdaptiveAIWidget = {
    open: () => toggleWidget(true),
    close: () => toggleWidget(false),
    toggle: () => toggleWidget(),
    ask: (question) => {
      toggleWidget(true);
      inputField.value = question;
      sendMessage();
    },
  };
})();
