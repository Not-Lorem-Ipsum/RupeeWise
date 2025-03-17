from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import google.generativeai as genai
import os
import warnings
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Ignore all warnings
warnings.filterwarnings("ignore")

# Configure the API key
GEMINI_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# Flask app
app = Flask(__name__)


def is_finance_related(message):
    """Check if the message is related to finance."""
    df = pd.read_csv("data/finance_keywords.csv", header=None)
    finance_keywords = pd.Series(df[0])
    return any(keyword in message.lower() for keyword in finance_keywords)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat_with_bot():
    user_message = request.json.get("message")

    if user_message.lower() in ["quit", "bye", "exit"]:
        return jsonify({"response": "Goodbye!"})

    if user_message.lower() == "history":
        return jsonify({"response": str(chat.history)})

    if not is_finance_related(user_message):
        return jsonify({"response": "Please ask finance-related questions only."})

    response = chat.send_message(user_message)
    return jsonify({"response": response.text})


if __name__ == '__main__':
    app.run(debug=True)
