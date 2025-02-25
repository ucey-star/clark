import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

function App() {
  const [response, setResponse] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [history, setHistory] = useState([]);
  const { transcript, listening, resetTranscript, startListening, stopListening } = useSpeechRecognition();

  // Request microphone permission on mount
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true }).catch((err) => {
      console.error("Microphone access denied:", err);
    });
  }, []);

  // Start listening function with proper options
  const handleStartListening = () => {
    if (!listening && !isSpeaking) {
      SpeechRecognition.startListening({ continuous: true, language: "en-US" });
    }
  };

  // Stop listening function
  const handleStopListening = () => {
    SpeechRecognition.stopListening();
  };

  const sendMessage = async () => {
    if (transcript && !isSpeaking) {
      handleStopListening(); // Stop listening before sending
      try {
        const res = await axios.post("http://127.0.0.1:5001/api/chat", {
          message: transcript,
          history: history, // Send chat history
        });

        setResponse(res.data.response);
        setHistory(res.data.history); // Update history

        speakResponse(res.data.response);
      } catch (error) {
        console.error("Error sending message:", error);
      }
      
      resetTranscript(); // Reset transcript after sending
    }
  };

  const speakResponse = (text) => {
    setIsSpeaking(true); // AI is speaking, so stop listening
    const utterance = new SpeechSynthesisUtterance(text);

    utterance.onstart = () => handleStopListening(); // Ensure recording stops while speaking
    utterance.onend = () => {
      setIsSpeaking(false); // AI finished speaking
      handleStartListening(); // Resume listening after speech synthesis
    };

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

      <motion.div
        animate={{ scale: listening ? [1, 1.2, 1] : 1 }}
        transition={{ duration: 0.5, repeat: Infinity }}
        style={{
          width: "100px",
          height: "100px",
          borderRadius: "50%",
          backgroundColor: listening ? "red" : "green",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "20px",
          color: "white",
          cursor: "pointer",
        }}
        onClick={listening ? handleStopListening : handleStartListening}
      >
        {listening ? "🎙️ Stop" : "🎤 Start"}
      </motion.div>

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
        disabled={isSpeaking} // Disable while AI is speaking
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "18px",
          background: isSpeaking ? "gray" : "blue",
          color: "white",
          border: "none",
          borderRadius: "10px",
          cursor: isSpeaking ? "not-allowed" : "pointer",
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
