from fastapi import FastAPI
import sqlite3
import requests
import os
from dotenv import load_dotenv
from llama_handler import create_index, query_index

# Load the .env file
load_dotenv()

# Fetch the API key from the environment
KINDO_API_KEY = os.getenv('KINDO_API_KEY')

app = FastAPI()

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

# API call to Kindo for generating a doctor summary
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

# API route to log symptoms
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

# API route to generate a doctor summary
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
