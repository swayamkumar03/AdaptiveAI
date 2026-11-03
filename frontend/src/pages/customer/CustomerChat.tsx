// src/pages/customer/CustomerChat.tsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  FileText,
  LogOut,
  Sparkles,
  HelpCircle,
} from 'lucide-react';
import { chatApi } from '../../api/chat';
import { feedbackApi } from '../../api/feedback';
import { authApi } from '../../api/auth';
import { useNavigate } from 'react-router-dom';
import { ChatMessage } from '../../types/api';

export const CustomerChat: React.FC = () => {
  const navigate = useNavigate();
  const currentUser = authApi.getCurrentUser();

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am your AI Support Assistant. How can I help you today with your inquiries?',
      created_at: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [feedbackSent, setFeedbackSent] = useState<Record<string, string>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleLogout = async () => {
    await authApi.logout();
    navigate('/login');
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(text, conversationId || undefined);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const botMsg: ChatMessage = {
        id: response.assistant_message_id,
        role: 'assistant',
        content: response.answer,
        confidence_score: response.confidence_score,
        is_escalated: response.is_escalated,
        sources: response.sources,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Sorry, I encountered an issue. Please try again.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (messageId: string, rating: 'POSITIVE' | 'NEGATIVE') => {
    try {
      setFeedbackSent((prev) => ({ ...prev, [messageId]: rating }));
      await feedbackApi.submitFeedback({
        message_id: messageId,
        rating,
      });
    } catch (err) {
      console.warn('Feedback failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-between">
      {/* Customer Header */}
      <header className="h-16 bg-slate-950/80 border-b border-slate-800 px-6 flex items-center justify-between backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">AdaptiveAI Customer Support</h1>
            <div className="flex items-center space-x-1.5 text-[11px] text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>Online • Instant AI Answers</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-semibold text-slate-200">{currentUser?.full_name}</p>
            <p className="text-[10px] text-slate-400">{currentUser?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      {/* Chat Messages Body */}
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 sm:p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-xs'
                  : 'bg-slate-800 text-slate-200 border border-slate-700/80 rounded-bl-xs'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>

              {/* Source citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-700/60 text-[11px] text-slate-400">
                  <div className="flex items-center space-x-1 font-semibold text-slate-300 mb-1">
                    <FileText className="w-3 h-3 text-blue-400" />
                    <span>Verified Knowledge Sources:</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {msg.sources.map((s, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/30 text-blue-300 text-[10px]"
                      >
                        {s.title || (s.source_type === 'verified_experience' ? 'Verified Experience' : 'Company Documentation')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Escalation Notification */}
              {msg.is_escalated && (
                <div className="mt-3 p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    Your inquiry has been escalated to a company representative for verification.
                  </span>
                </div>
              )}

              {/* Helpful Feedback */}
              {msg.role === 'assistant' && msg.id !== 'welcome' && (
                <div className="mt-2.5 pt-2 border-t border-slate-700/40 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Was this answer helpful?</span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleFeedback(msg.id, 'POSITIVE')}
                      disabled={!!feedbackSent[msg.id]}
                      className={`p-1 rounded hover:text-white transition ${
                        feedbackSent[msg.id] === 'POSITIVE'
                          ? 'text-emerald-400'
                          : 'text-slate-400'
                      }`}
                      title="Yes, helpful"
                    >
                      <ThumbsUp className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleFeedback(msg.id, 'NEGATIVE')}
                      disabled={!!feedbackSent[msg.id]}
                      className={`p-1 rounded hover:text-white transition ${
                        feedbackSent[msg.id] === 'NEGATIVE'
                          ? 'text-rose-400'
                          : 'text-slate-400'
                      }`}
                      title="No, not helpful"
                    >
                      <ThumbsDown className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 p-2 bg-slate-800/60 rounded-xl w-fit border border-slate-700/60">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></div>
            <span>AI Assistant is analyzing company knowledge...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Input Footer */}
      <footer className="p-4 bg-slate-950/80 border-t border-slate-800 backdrop-blur-md sticky bottom-0">
        <form
          onSubmit={handleSend}
          className="max-w-3xl mx-auto flex items-center space-x-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            disabled={loading}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-hidden focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 transition cursor-pointer shadow-md shadow-blue-500/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </footer>
    </div>
  );
};
export default CustomerChat;
