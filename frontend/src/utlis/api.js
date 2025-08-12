export const sendMessage = async (sessionId, message) => {
  const res = await fetch('https://signize-backend.onrender.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  return res.json();
};