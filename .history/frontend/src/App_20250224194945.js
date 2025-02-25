import React, { useState } from "react";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

function App() {
  const [response, setResponse] = useState("");
  const { transcript, listening, resetTranscript, startListening, stopListening } = useSpeechRecognition();

  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return <span>Your browser does not support speech recognition.</span>;
  }

  const sendMessage = async () => {
    if (transcript) {
      const res = await axios.post("http://127.0.0.1:5000/api/chat", { message: transcript });
      setResponse(res.data.response);
      speakResponse(res.data.response);
      resetTranscript();
    }
  };

  const speakResponse = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
  };

  return (
    <div style={{ 
      background: "black", 
      height: "100vh", 
      display: "flex", 
      flexDirection: "column", 
      justifyContent: "center", 
      alignItems: "center", 
      color: "white",
      fontFamily: "Arial, sans-serif",
    }}>
      <h2>🎤 AI Voice Assistant</h2>

      <button 
        onClick={listening ? stopListening : startListening} 
        style={{
          padding: "15px 30px",
          fontSize: "20px",
          background: listening ? "red" : "green",
          color: "white",
          border: "none",
          borderRadius: "10px",
          cursor: "pointer",
          transition: "background 0.3s"
        }}
      >
        {listening ? "Stop Listening" : "Start Talking"}
      </button>

      <div style={{
        marginTop: "20px",
        fontSize: "24px",
        fontWeight: "bold",
        color: "#00FF00"
      }}>
        {transcript}
      </div>

      <button 
        onClick={sendMessage} 
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "18px",
          background: "blue",
          color: "white",
          border: "none",
          borderRadius: "10px",
          cursor: "pointer",
          transition: "background 0.3s"
        }}
      >
        Send to AI
      </button>

      <p style={{ marginTop: "20px", fontSize: "20px", color: "#FFD700" }}>
        {response}
      </p>
    </div>
  );
}

export default App;
