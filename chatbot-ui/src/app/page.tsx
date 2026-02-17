'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm SmartOhm customer support assistant. How can I help you with your queries?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const data = await response.json();

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble connecting to my brain right now. Please make sure the backend server is running.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="status-dot"></div>
        <h1>SMARTOHM ASSISTANT</h1>
      </div>

      <div className="messages-area">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {isLoading && (
          <div className="typing-indicator">Assistant is thinking...</div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about returns, shipping, or styles..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={isLoading}
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
