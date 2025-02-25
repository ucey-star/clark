from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv 

load_dotenv()
# Load API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

@app.route("/")
def index():
    return "AI Assistant Backend is running!"

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
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o or any available model
            messages=[
                {"role": "system", "content": "You are an AI assistant responding to voice commands."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )
        ai_response = response["choices"][0]["message"]["content"]
        return jsonify({"response": ai_response})

    except Exception as e:
        print("error", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
