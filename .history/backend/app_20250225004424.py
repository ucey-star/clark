from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv 
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

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
    creds = get_credentials()  # Use the function that reuses or refreshes the token
    service = build("gmail", "v1", credentials=creds)

    if action == "read_emails":
        try:
            # Fetch up to 5 recent messages
            results = service.users().messages().list(userId="me", maxResults=5).execute()
            messages = results.get("messages", [])

            if not messages:
                return "You have no unread emails."

            cleaned_emails = []
            for i, msg in enumerate(messages, start=1):
                msg_data = service.users().messages().get(
                    userId="me", 
                    id=msg["id"], 
                    format="metadata",
                    metadataHeaders=["Subject","From","Date"]
                ).execute()

                # Extract desired headers
                headers = msg_data.get("payload", {}).get("headers", [])
                
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject"
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown sender"
                )
                date_str = next(
                    (h["value"] for h in headers if h["name"] == "Date"),
                    "Unknown date"
                )

                # You can still get the snippet (short body preview)
                snippet = msg_data.get("snippet", "")
                # Optionally truncate the snippet to avoid large outputs
                if len(snippet) > 120:
                    snippet = snippet[:120] + "..."

                # Format a brief summary for each email
                email_summary = (
                    f"**Email {i}**\n"
                    f"• **Subject:** {subject}\n"
                    f"• **From:** {sender}\n"
                    f"• **Date:** {date_str}\n"
                    f"• **Snippet:** {snippet}\n"
                )
                cleaned_emails.append(email_summary)

            # Join all summaries in a neat block
            return "\n".join(cleaned_emails)

        except Exception as e:
            return f"Error fetching emails: {e}"

    elif action == "send_email":
        return f"Sending email with subject: {email_subject}"

    else:
        return "Unknown email action."

    

# def handle_calendar_action(action, event_details=None):
#     """
#     Function to handle calendar-related tasks.
#     """
#     if action == "check_schedule":
#         return "You have a meeting tomorrow at 10 AM."
#     elif action == "create_event":
#         return f"Adding event: {event_details}"
#     else:
#         return "Unknown calendar action."

def handle_calendar_action(action, event_details=None):
    """
    Perform calendar-related actions like checking upcoming events or scheduling new ones.
    """
    creds = get_credentials()  # Use the function that reuses or refreshes the token
    service = build("gmail", "v1", credentials=creds)

    if action == "check_schedule":
        try:
            events_result = service.events().list(
                calendarId="primary",
                maxResults=5,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])

            event_list = []
            for event in events:
                summary = event.get("summary", "No Title")
                start = event["start"].get("dateTime", event["start"].get("date"))
                event_list.append(f"📅 {summary} at {start}")

            return "\n".join(event_list) if event_list else "You have no upcoming events."

        except Exception as e:
            return f"Error fetching calendar events: {e}"

    elif action == "create_event":
        return f"Adding event: {event_details}"

    else:
        return "Unknown calendar action."



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
            elif function_name == "handle_calendar_action":
                ai_response = handle_calendar_action(**arguments)
            else:
                ai_response = "Unknown function request."
        else:
            ai_response = response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": ai_response})
        return jsonify({"response": ai_response})

    except Exception as e:
        print("error", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)

