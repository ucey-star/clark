from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv 
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import texttospeech
import uuid  # Add this to fix the NameError
from datetime import datetime, timezone


load_dotenv()
# Load API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests
# Set up Google API credentials
SERVICE_ACCOUNT_FILE = "credentials.json"
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar"
]

# credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# # Initialize Gmail & Calendar API clients
# gmail_service = build("gmail", "v1", credentials=credentials)
# calendar_service = build("calendar", "v3", credentials=credentials)
AUDIO_DIR = "audio_responses"
os.makedirs(AUDIO_DIR, exist_ok=True)  # Ensure directory exists

conversation_history = []

KNOWLEDGE_BASE = """
You are a personalized AI assistant named Clark.
You were created by Uchechukwu Unanka, a talented software engineer and AI developer.
Your goal is to assist Uchechukwu with coding, research, daily tasks, and general productivity.
You can remember details about previous conversations within a session, but do not retain data permanently.

Your creator, Uchechukwu, is based in San Francisco and has expertise in AI, software engineering, and startups.
He has worked at top tech companies like Asana and Uber and has developed projects in machine learning, web development, and cloud infrastructure.

If asked about yourself, respond as Clark, and if asked about your creator, provide details about Uchechukwu.
When responding to questions, keep context in mind based on past conversations.
"""

@app.route("/")
def index():
    return "AI Assistant Backend is running!"

def get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid creds, either refresh or run new OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )
            # Use extra arguments to ensure refresh token is provided
            creds = flow.run_local_server(
                port=5000,
                redirect_uri_trailing_slash=False,
                access_type='offline',
                prompt='consent'
            )

        # Save credentials to token.json
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

def speak_response_google(text):
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D",  # Male voice
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(AUDIO_DIR, filename)

    # Save the file
    with open(file_path, "wb") as out:
        out.write(response.audio_content)

    print(f"✅ Audio file generated: {file_path}")  # Debugging

    return filename  # Return the filename, NOT the full path


# Function mapping for Clark
# def handle_email_action(action, email_subject=None, email_body=None):
#     """
#     Function to handle email-related tasks.
#     """
#     if action == "read_emails":
#         return "You have 5 unread emails."
#     elif action == "send_email":
#         return f"Sending email with subject: {email_subject}"
#     else:
#         return "Unknown email action."
# **🔹 Email Functions**
def handle_email_action(action, email_subject=None, email_body=None):
    """
    Perform email-related actions such as reading recent emails or sending emails.
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    if action == "read_emails":
        try:
            results = service.users().messages().list(userId="me", maxResults=5).execute()
            messages = results.get("messages", [])

            if not messages:
                return "You have no new emails."

            cleaned_emails = []
            for i, msg in enumerate(messages, start=1):
                msg_data = service.users().messages().get(
                    userId="me", 
                    id=msg["id"], 
                    format="metadata",
                    metadataHeaders=["Subject","From","Date"]
                ).execute()

                headers = msg_data.get("payload", {}).get("headers", [])
                
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown sender")
                date_str = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown date")
                snippet = msg_data.get("snippet", "")
                snippet = snippet[:120] + "..." if len(snippet) > 120 else snippet

                email_summary = f"Email {i}: From {sender}, Subject: {subject}, Date: {date_str}. Summary: {snippet}"
                cleaned_emails.append(email_summary)

            raw_response = "\n".join(cleaned_emails)
            return format_with_gpt4(raw_response)  # ✅ Clean with GPT-4

        except Exception as e:
            return f"Error fetching emails: {e}"

    elif action == "send_email":
        return f"Sending email with subject: {email_subject}"

    else:
        return "Unknown email action."


def handle_calendar_action(action, event_details=None):
    """
    Perform calendar-related actions like checking upcoming events or scheduling new ones.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    if action == "check_schedule":
        try:
            now = datetime.now(timezone.utc).isoformat()
            events_result = service.events().list(
                calendarId="primary",
                timeMin=now,  # ✅ Get only future events
                maxResults=5,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            if not events:
                return "You have no upcoming events."

            event_list = []
            for event in events:
                summary = event.get("summary", "No Title")
                start = event["start"].get("dateTime", event["start"].get("date"))
                event_list.append(f"{summary} on {start}")

            raw_response = "\n".join(event_list)
            return format_with_gpt4(raw_response)  # ✅ Clean with GPT-4

        except Exception as e:
            return f"Error fetching calendar events: {e}"

    elif action == "create_event":
        return f"Adding event: {event_details}"

    else:
        return "Unknown calendar action."



def format_with_gpt4(raw_text):
    """
    Uses OpenAI's GPT-4 to clean up the response and make it more readable for voice output.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Format this response for a voice assistant. Make it clear, short, and natural to read aloud."},
                {"role": "user", "content": raw_text}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error formatting with GPT-4: {e}")
        return raw_text  # Return raw text if formatting fails


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Receives text from frontend, sends it to OpenAI API, and returns the response.
    """
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        print("user_message", user_message)

        conversation_history.append({"role": "user", "content": user_message})
        conversation_history[:] = conversation_history[-100:]
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o or any available model
            messages=[
                {"role": "system", "content": KNOWLEDGE_BASE},
                {"role": "user", "content": user_message}
            ] + conversation_history,
            functions=[
                {
                    "name": "handle_email_action",
                    "description": "Perform actions related to emails",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["read_emails", "send_email"]},
                            "email_subject": {"type": "string"},
                            "email_body": {"type": "string"},
                        },
                        "required": ["action"]
                    }
                },
                {
                    "name": "handle_calendar_action",
                    "description": "Perform actions related to calendar events",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["check_schedule", "create_event"]},
                            "event_details": {"type": "string"},
                        },
                        "required": ["action"]
                    }
                }
            ],
            function_call="auto",
            max_tokens=2000
        )
        if response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            arguments = json.loads(response.choices[0].message.function_call.arguments)

            if function_name == "handle_email_action":
                ai_response = handle_email_action(**arguments)
                audio_file = speak_response_google(ai_response)
            elif function_name == "handle_calendar_action":
                ai_response = handle_calendar_action(**arguments)
                audio_file = speak_response_google(ai_response)
            else:
                ai_response = "Unknown function request."
                audio_file = speak_response_google(ai_response)
        else:
            ai_response = response.choices[0].message.content
            audio_file = speak_response_google(ai_response)

        conversation_history.append({"role": "assistant", "content": ai_response})
        return jsonify({"response": ai_response, "audio": audio_file})

    except Exception as e:
        print("error", e)
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<filename>")
def get_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)  # Ensure the correct directory is used

if __name__ == "__main__":
    app.run(debug=True, port=5001)

