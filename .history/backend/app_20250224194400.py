from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # Simple AI response (Replace with OpenAI API later)
    response = f"AI Assistant: You said '{user_message}'"

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
