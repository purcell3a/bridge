from app.llama_handler import query_index, create_index
from app.utils import call_kindo_api
from app.auth import get_current_user
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Symptom logging route (protected)
def log_symptom(symptom: str, current_user: dict):
    user_id = current_user["id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO symptoms (user_id, symptom, timestamp) VALUES (?, ?, datetime('now'))", (user_id, symptom))
    conn.commit()
    conn.close()

    # Optionally update LlamaIndex in real-time
    create_index(user_id)
    
    return {"status": "Symptom logged successfully"}

# Doctor summary generation route (protected)
def generate_summary(symptom_input: str, current_user: dict):
    user_id = current_user["id"]
    historical_data = query_index(user_id)

    current_input = symptom_input.current_symptoms
    combined_input = f"{current_input}\nHistorical data: {historical_data}"

    kindo_response = call_kindo_api(combined_input)
    
    return {"summary": kindo_response}
