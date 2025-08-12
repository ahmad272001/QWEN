import { useState } from 'react';
import { sendMessage } from '../utils/api';

export default function ChatWindow({ onClose, onMinimize }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('sessionId') || null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const id = sessionId || Date.now().toString();
    if (!sessionId) {
      setSessionId(id);
      localStorage.setItem('sessionId', id);
    }

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const res = await sendMessage(id, input);
    setMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
    setLoading(false);
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      width: '380px',
      height: '500px',
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 1000,
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '12px',
        backgroundColor: '#6a3dff',
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <strong>Signize Support</strong>
        <div>
          <button onClick={onMinimize} style={{ background: 'none', border: 'none', color: 'white', marginRight: '8px' }}>−</button>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'white' }}>✕</button>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            margin: '8px 0',
            textAlign: msg.role === 'user' ? 'right' : 'left'
          }}>
            <span style={{
              display: 'inline-block',
              padding: '8px 12px',
              borderRadius: '18px',
              backgroundColor: msg.role === 'user' ? '#6a3dff' : '#f1f1f1',
              color: msg.role === 'user' ? 'white' : 'black',
              maxWidth: '80%'
            }}>
              {msg.content}
            </span>
          </div>
        ))}
        {loading && <div style={{ textAlign: 'left', padding: '0 10px' }}>💬 Typing...</div>}
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', padding: '8px', borderTop: '1px solid #eee' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: '8px', border: '1px solid #ccc', borderRadius: '20px', outline: 'none' }}
        />
        <button type="submit" style={{ marginLeft: '8px', padding: '8px 12px', backgroundColor: '#6a3dff', color: 'white', border: 'none', borderRadius: '20px' }}>
          Send
        </button>
      </form>
    </div>
  );
}