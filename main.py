from fastapi import FastAPI, HTTPException
import sqlite3
import requests
import os
from dotenv import load_dotenv
from llama_handler import create_index, query_index

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

# API call to Kindo for generating a doctor summary
def call_kindo_api(combined_input):
    url = "https://llm.kindo.ai/v1/chat/completions"
    
    # Get the API key from the environment variables
    api_key = os.getenv("KINDO_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Kindo API key not found in environment variables")
    
    headers = {
        "api-key": api_key,  # Use the API key from environment
        "Content-Type": "application/json"
    }
    payload = {
        "model": "YOUR_MODEL_NAME",  # Replace with actual model name from Kindo
        "messages": [{"role": "user", "content": combined_input}],
        "max_tokens": 500
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad Request: Invalid input")
    elif response.status_code == 401:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key")
    elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")
    elif response.status_code == 429:
        raise HTTPException(status_code=429, detail="Too Many Requests: Rate limit exceeded")
    else:
        raise HTTPException(status_code=500, detail="Kindo API server error")

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
