from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os
import pandas as pd
import warnings

# Load environment variables from .env file
load_dotenv()

# Ignore warnings to avoid cluttered console output
warnings.filterwarnings("ignore")

# Configure the Gemini AI API key from environment variables
GEMINI_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini AI model
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# Create a Flask web application
app = Flask(__name__)

# Set a random secret key for session management
app.secret_key = os.urandom(24)

def is_finance_related(message):
    """
    Check if the user message is finance-related.
    Reads finance-related keywords from a CSV file and checks if any of them are in the message.
    """
    df = pd.read_csv("data/finance_keywords.csv", header=None)
    finance_keywords = pd.Series(df[0])  # Extract keywords from the first column
    return any(keyword in message.lower() for keyword in finance_keywords)

@app.before_request
def init_session():
    """Initialize session storage for user data if not already present."""
    if "users" not in session:
        session["users"] = {}  

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/faq', methods=['GET','POST'])
def faq():
    if request.method=='POST':
        return render_template('ChatBot.html')
    return render_template('faq.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    If the user exists and credentials are correct, log them in.
    Otherwise, display an appropriate error message.
    """
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        # Check if user exists
        if username in session["users"]:
            # Validate password
            if session["users"][username]["password"] == password:
                session["user"] = username  # Store the logged-in username in session
                return render_template('ChatBot.html')
            else:
                flash("Invalid username or password.", "error")
                return render_template('login.html')
        else:
            flash("Account does not exist.", "error")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup.
    Validate input fields and ensure email format is correct.
    If the user already exists, prevent duplicate accounts.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validate email format
        if '@' not in email:
            flash("Incorrect email address.", "error")
            return redirect(url_for('signup'))

        # Validate name (should contain only alphabets and spaces)
        if not name.replace(" ", "").isalpha():
            flash("Incorrect name.", "error")
            return redirect(url_for("signup"))

        username = email.split('@')[0]  # Generate username from email prefix

        # Check if username already exists
        if username in session['users']:
            flash("Account already exists! Please log in.", "error")
            return redirect(url_for('signup'))
        else:
            # Store user data in session
            session['users'][username] = {"email": email, "password": password}
            session.modified = True  # Mark session as modified
            flash(f"Account created successfully! Your username is '{username}'. Please log in.", "success")
            return redirect(url_for('login'))

    return render_template("signup.html")

@app.route('/chat', methods=['POST'])
def chat_with_bot():
    """
    Handle chatbot interactions.
    - Exit on "quit", "bye", or "exit".
    - Show chat history on "history" command.
    - Respond only to finance-related questions.
    """
    user_message = request.json.get("message")

    # Exit chat
    if user_message.lower() in ["quit", "bye", "exit"]:
        return jsonify({"response": "Goodbye!"})

    # Show chat history
    if user_message.lower() == "history":
        return jsonify({"response": str(chat.history)})

    # Restrict chatbot to finance-related topics
    if not is_finance_related(user_message):
        return jsonify({"response": "Please ask finance-related questions only."})

    # Generate AI response
    response = chat.send_message(user_message)
    return jsonify({"response": response.text})

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
