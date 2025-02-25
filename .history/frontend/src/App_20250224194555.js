import React, { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const sendMessage = async () => {
    const res = await axios.post("http://127.0.0.1:5000/api/chat", { message });
    setResponse(res.data.response);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>AI Assistant</h2>
      <input 
        type="text" 
        value={message} 
        onChange={(e) => setMessage(e.target.value)} 
        placeholder="Ask me anything..."
      />
      <button onClick={sendMessage}>Send</button>
      <p><strong>{response}</strong></p>
    </div>
  );
}

export default App;
