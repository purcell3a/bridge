import os
import sqlite3
from fastapi import FastAPI, HTTPException
from llama_handler import create_index, query_index
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Fetch API key for Kindo API
KINDO_API_KEY = os.getenv('KINDO_API_KEY')

# Create FastAPI app instance
app = FastAPI()

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

# Function to create a user
@app.post("/create-user")
def create_user(name: str, email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert user into the users table
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

    return {"status": "User created successfully", "name": name, "email": email}

# Function to get a user by ID
@app.get("/get-user/{user_id}")
def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the database for the user
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    # If user does not exist, raise a 404 error
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the user data
    return {"id": user[0], "name": user[1], "email": user[2]}

# Symptom logging route
@app.post("/log-symptom")
def log_symptom(symptom: str, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO symptoms (user_id, symptom, timestamp) VALUES (?, ?, datetime('now'))", (user_id, symptom))
    conn.commit()
    conn.close()

    # Optionally update LlamaIndex in real-time
    create_index(user_id)
    
    return {"status": "Symptom logged successfully"}

# Doctor summary generation route
@app.get("/generate-summary")
def generate_summary(user_id: int):
    # Query LlamaIndex for relevant historical symptoms
    historical_data = query_index(user_id)
    
    # Combine historical data with current symptoms (you can modify this)
    current_input = "User reports frequent headaches and nausea."
    combined_input = f"{current_input}\nHistorical data: {historical_data}"

    # Call Kindo API to generate the summary
    kindo_response = call_kindo_api(combined_input)
    
    return {"summary": kindo_response}

# Kindo API call
def call_kindo_api(combined_input):
    url = "https://kindo-api-endpoint/chat/completions"
    headers = {
        "Authorization": f"Bearer {KINDO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": combined_input,
        "max_tokens": 500
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
