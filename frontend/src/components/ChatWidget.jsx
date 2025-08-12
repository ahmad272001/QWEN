import { useState } from 'react';
import ThreeDFloatingChat from './ThreeDFloatingIcon';
import ChatWindow from './ChatWindow';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const toggleChat = () => setIsOpen(!isOpen);
  const minimizeChat = () => setIsMinimized(!isMinimized);

  if (!isOpen) return <ThreeDFloatingChat onOpen={toggleChat} />;

  if (isMinimized) {
    return (
      <div
        onClick={minimizeChat}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          backgroundColor: '#6a3dff',
          color: 'white',
          padding: '10px 15px',
          borderRadius: '8px',
          cursor: 'pointer',
          zIndex: 1000,
          boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
        }}
      >
        💬 Support
      </div>
    );
  }

  return <ChatWindow onClose={toggleChat} onMinimize={minimizeChat} />;
}