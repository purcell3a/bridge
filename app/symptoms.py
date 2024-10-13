from fastapi import APIRouter, Depends, HTTPException
from app.llama_handler import query_index, create_index
from app.auth import get_current_user
from database.database import get_db_connection

router = APIRouter()

# Symptom logging route (protected)
@router.post("/log-symptom", summary="Log Symptom", description="Logs a symptom for the current user")
def log_symptom(symptom: str, current_user: dict = Depends(get_current_user)):
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
@router.post("/generate-summary", summary="Generate Summary", description="Generates a doctor summary based on symptoms")
def generate_summary(symptom_input: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    historical_data = query_index(user_id)

    combined_input = f"{symptom_input}\nHistorical data: {historical_data}"

    # Call the Kindo API to generate the summary
    kindo_response = call_kindo_api(combined_input)
    
    return {"summary": kindo_response}
