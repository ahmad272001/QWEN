import React from 'react';
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div className="App">
      {/* Your website content would go here */}
      <main style={{ minHeight: '100vh', padding: '20px' }}>
        <h1>Welcome to Signize</h1>
        <p>Custom 3D signage for your business. Need help? Chat with our AI assistant!</p>
      </main>

      {/* 3D Floating Chat Widget */}
      <ChatWidget />
    </div>
  );
}

export default App;