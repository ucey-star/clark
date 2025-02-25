from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv 
import json

load_dotenv()
# Load API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

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

# Function mapping for Clark
def handle_email_action(action, email_subject=None, email_body=None):
    """
    Function to handle email-related tasks.
    """
    if action == "read_emails":
        return "You have 5 unread emails."
    elif action == "send_email":
        return f"Sending email with subject: {email_subject}"
    else:
        return "Unknown email action."

def handle_calendar_action(action, event_details=None):
    """
    Function to handle calendar-related tasks.
    """
    if action == "check_schedule":
        return "You have a meeting tomorrow at 10 AM."
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
    app.run(debug=True, port=5000)
