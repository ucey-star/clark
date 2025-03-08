
import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";

// Simple inline SVG for a microphone icon
function MicIcon({ fill = "currentColor", size = 24 }) {
  return (
    <svg
      style={{ marginRight: "0.5rem" }}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={fill}
    >
      <path d="M12 15c1.654 0 3-1.346 3-3V7a3 3 0 10-6 0v5c0 1.654 1.346 3 3 3z"></path>
      <path d="M19 10a1 1 0 00-2 0 5 5 0 01-10 0 1 1 0 00-2 0 7 7 0 006 6.93V19H8a1 1 0 000 2h8a1 1 0 000-2h-3v-2.07A7 7 0 0019 10z"></path>
    </svg>
  );
}

function App() {
  // State
  const [response, setResponse] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [history, setHistory] = useState([]);

  // “mode” = "idle", "wakeWord", or "command"
  const [mode, setMode] = useState("idle");

  // Partial transcripts, etc.
  const [lastTranscript, setLastTranscript] = useState("");
  const [lastChangeTime, setLastChangeTime] = useState(Date.now());

  // Guard to prevent multiple sends from partial transcripts
  const hasSentCommand = useRef(false);

  const {
    transcript,
    listening,
    resetTranscript,
    startListening,
    stopListening,
  } = useSpeechRecognition();

  // Confirmation Ding
  const confirmSound = useRef(null);

  /////////////////////////////////////////////////////////////////////////////
  // STYLES
  /////////////////////////////////////////////////////////////////////////////
  const appStyles = {
    background: "linear-gradient(to bottom right, #161616, #1f1f1f)",
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    fontFamily: "'Open Sans', sans-serif",
    color: "#ffffff",
    margin: 0,
    padding: 0,
  };

  const containerStyles = {
    width: "90%",
    maxWidth: "600px",
    backgroundColor: "#2c2c2c",
    padding: "2rem",
    borderRadius: "12px",
    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.25)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  };

  const headingStyles = {
    marginBottom: "1rem",
    fontSize: "1.8rem",
    fontWeight: "600",
    textAlign: "center",
  };

  // Updated mic button to a rectangular style with an icon + text
  const micButtonStyles = (isMicActive) => ({
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "0.75rem 1.25rem",
    borderRadius: "8px",
    border: "none",
    outline: "none",
    cursor: "pointer",
    marginTop: "1rem",
    color: "#fff",
    fontSize: "1rem",
    fontWeight: "600",
    background: isMicActive ? "#d32f2f" : "#388e3c",
    boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
    transition: "background 0.3s",
  });

  const transcriptStyles = {
    marginTop: "1.5rem",
    padding: "1rem",
    fontSize: "1.1rem",
    fontWeight: "bold",
    color: "#00FF00",
    backgroundColor: "#1a1a1a",
    borderRadius: "6px",
    minHeight: "60px",
    width: "100%",
    textAlign: "left",
    boxSizing: "border-box",
    overflowWrap: "break-word",
  };

  const buttonStyles = (disabled) => ({
    marginTop: "1.5rem",
    padding: "0.75rem 1.5rem",
    fontSize: "1rem",
    background: disabled ? "#555" : "#1976d2",
    color: "#fff",
    borderRadius: "8px",
    border: "none",
    cursor: disabled ? "not-allowed" : "pointer",
    outline: "none",
    transition: "background 0.3s",
  });

  const responseStyles = {
    marginTop: "1.5rem",
    fontSize: "1.1rem",
    color: "#ffd700",
    textAlign: "center",
    wordWrap: "break-word",
  };

  /////////////////////////////////////////////////////////////////////////////
  // AUDIO SETUP & PERMISSIONS
  /////////////////////////////////////////////////////////////////////////////
  useEffect(() => {
    confirmSound.current = new Audio("ding.mp3");
  }, []);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .catch((err) => console.error("Mic access denied:", err));
  }, []);

  /////////////////////////////////////////////////////////////////////////////
  // MODE HANDLING
  /////////////////////////////////////////////////////////////////////////////
  const handleStartButtonClick = () => {
    // Unlock audio
    confirmSound.current.play().catch((e) => console.warn("Audio unlock error:", e));
    confirmSound.current.pause();
    confirmSound.current.currentTime = 0;

    setMode("wakeWord");
    startWakeWordListening();
  };

  const startWakeWordListening = () => {
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-US",
      interimResults: true,
    });
  };

  const startCommandListening = () => {
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-US",
      interimResults: true,
    });
  };

  const handleStopListening = () => {
    SpeechRecognition.stopListening();
  };

  /////////////////////////////////////////////////////////////////////////////
  // WAKE WORD DETECTION
  /////////////////////////////////////////////////////////////////////////////
  useEffect(() => {
    if (mode === "wakeWord" && transcript.toLowerCase().includes("hey clark")) {
      confirmSound.current.currentTime = 0;
      confirmSound.current.play().catch((e) => console.warn("ding error:", e));

      setMode("command");
      resetTranscript();
      hasSentCommand.current = false; // reset guard
      startCommandListening();
    }
  }, [transcript, mode, resetTranscript]);

  /////////////////////////////////////////////////////////////////////////////
  // TRIGGER WORD DETECTION: "that's all"
  /////////////////////////////////////////////////////////////////////////////
  useEffect(() => {
    if (mode === "command" && !hasSentCommand.current) {
      if (transcript !== lastTranscript) {
        setLastTranscript(transcript);
        setLastChangeTime(Date.now());
      }
      if (transcript.toLowerCase().includes("that's all")) {
        hasSentCommand.current = true;
        handleStopListening();

        const cleanedTranscript = transcript
          .toLowerCase()
          .replace("that's all", "")
          .trim();
        if (cleanedTranscript.length > 0) {
          sendMessage(cleanedTranscript);
        } else {
          sendMessage();
        }
      }
    }
  }, [transcript, mode, lastTranscript]);

  /////////////////////////////////////////////////////////////////////////////
  // SEND MESSAGE TO AI
  /////////////////////////////////////////////////////////////////////////////
  const sendMessage = async (overrideMessage) => {
    const finalMessage = overrideMessage !== undefined ? overrideMessage : transcript;
    if (!finalMessage || isSpeaking) return;

    handleStopListening();
    try {
      const res = await axios.post("http://127.0.0.1:5001/api/chat", {
        message: finalMessage,
        history,
      });
      setResponse(res.data.response);
      setHistory(res.data.history);
      playResponse(res.data.audio);
    } catch (error) {
      console.error("Error sending message:", error);
    }
    resetTranscript();
  };

  /////////////////////////////////////////////////////////////////////////////
  // PLAY AI RESPONSE AUDIO
  /////////////////////////////////////////////////////////////////////////////
  const playResponse = (audioUrl) => {
    setIsSpeaking(true);
    const audio = new Audio(`http://127.0.0.1:5001/audio/${audioUrl}`);

    audio.onended = () => {
      setIsSpeaking(false);
      setMode("wakeWord");
      resetTranscript();
      startWakeWordListening();
    };

    audio.play().catch((e) => console.warn("AI audio play error:", e));
  };

  /////////////////////////////////////////////////////////////////////////////
  // Fallback if browser doesn’t support speech recognition
  /////////////////////////////////////////////////////////////////////////////
  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return (
      <div style={{ ...appStyles, padding: "2rem" }}>
        <p>Browser does not support speech recognition.</p>
      </div>
    );
  }

  /////////////////////////////////////////////////////////////////////////////
  // RENDER
  /////////////////////////////////////////////////////////////////////////////
  return (
    <div style={appStyles}>
      <div style={containerStyles}>
        <h2 style={headingStyles}>Hey Clark - Voice Assistant</h2>

        {mode === "idle" && (
          <button onClick={handleStartButtonClick} style={buttonStyles(false)}>
            Start
          </button>
        )}

        {mode !== "idle" && (
          <>
            {/* Replaced the old circular mic button with a modern rectangular toggle */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={micButtonStyles(listening)}
              onClick={listening ? handleStopListening : startCommandListening}
            >
              <MicIcon size={20} />
              {listening ? "Listening..." : "Speak"}
            </motion.button>

            {/* Transcript Display */}
            <div style={transcriptStyles}>{transcript}</div>

            {/* Manual “Send” Button (optional) */}
            <button
              onClick={() => sendMessage()}
              disabled={isSpeaking}
              style={buttonStyles(isSpeaking)}
            >
              Send to AI
            </button>

            {/* AI Text Response */}
            {response && <p style={responseStyles}>{response}</p>}
          </>
        )}
      </div>
    </div>
  );
}

export default App;