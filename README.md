# Clark AI Assistant

Clark is a **voice-powered AI assistant** that can process and respond to voice commands, manage emails and calendar events, and provide text-to-speech responses. Designed to be **fully interactive**, Clark listens for the wake word and can engage in meaningful conversations, integrating **GPT-4** for natural language processing and **Google APIs** for handling emails and calendars.

## Features 🚀

- **Voice Activation**: Listens for a wake word (e.g., "Hey Clark") to start processing commands.
- **Speech Recognition**: Uses **Web Speech API** for real-time voice-to-text conversion.
- **Natural Conversations**: Powered by **GPT-4** to generate human-like responses.
- **Email Integration**: Reads and summarizes Gmail messages.
- **Calendar Management**: Retrieves upcoming events and can schedule new ones.
- **Text-to-Speech (TTS)**: Converts AI-generated responses into natural speech using **Google Cloud Text-to-Speech**.
- **Cross-Platform UI**: Built with **React & Flask**, enabling seamless communication between the frontend and backend.

---

## Installation & Setup 🛠️

### **Prerequisites**
Ensure you have the following installed:
- **Python 3.8+**
- **Node.js 16+** (for the frontend)
- **Google Cloud API Access** (Enable Gmail, Calendar, and Text-to-Speech APIs)
- **OpenAI API Key**

### **1. Clone the Repository**
```sh
 git clone https://github.com/yourusername/clark-ai.git
 cd clark-ai
```

### **2. Set Up the Backend**
```sh
cd backend
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### **Configure Environment Variables**
Create a `.env` file in the `backend/` directory and add:
```ini
OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```

#### **Run the Backend Server**
```sh
python app.py
```
> The server runs at **http://127.0.0.1:5001**

---

### **3. Set Up the Frontend**
```sh
cd ../frontend
npm install
npm start
```
> The frontend runs at **http://localhost:3000**

---

## Usage 🗣️
1. Open the web app.
2. Say **"Hey Clark"** to activate voice recognition.
3. Give commands like:
   - *"Check my email"*
   - *"What's on my calendar today?"*
   - *"Send an email to John about our meeting."*
4. Clark will **speak back responses** using Google TTS.

---

## API Endpoints 📡
### **1. Chat API**
**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "Check my email"
}
```

**Response:**
```json
{
  "response": "You have 3 unread emails.",
  "audio": "response.mp3"
}
```

### **2. Email Actions**
**Read Emails:**
```json
{
  "action": "read_emails"
}
```

### **3. Calendar Actions**
**Check Schedule:**
```json
{
  "action": "check_schedule"
}
```

---

## Technologies Used 🛠️
- **Backend:** Flask, OpenAI API, Google Cloud APIs
- **Frontend:** React.js, Framer Motion, Axios, Web Speech API
- **Speech Processing:** Google Cloud Text-to-Speech

---

## Contributors 🤝
- **Uchechukwu Unanka** – Creator & Lead Developer

---

## License 📜
This project is licensed under the MIT License.

