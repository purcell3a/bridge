from fastapi import APIRouter, Depends, HTTPException
from app.llama_handler import query_index, create_index
from app.auth import get_current_user
from database.database import get_db_connection

router = APIRouter()

# Symptom logging route (protected)
@router.post("/log-symptom", summary="Log Symptom", description="Logs a symptom and generates a Kindo-based response")
def log_symptom(symptom: str, current_user: dict = Depends(get_current_user)):
    """
    Logs the user's symptom and generates a dynamic response from Kindo API.
    """
    # Log the symptom to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO symptoms (user_id, symptom, timestamp) VALUES (?, ?, datetime('now'))", (1, symptom))
    conn.commit()
    conn.close()

    # Optionally update LlamaIndex in real-time
    create_index(1)  # Assuming static user_id for now

    # Call Kindo API to generate a dynamic follow-up response based on the symptom
    kindo_response = call_kindo_api(symptom)

    # Return success message, logged symptom, and Kindo's dynamic follow-up response
    return {
        "status": "Symptom logged successfully",
        "logged_symptom": symptom,
        "followup_response": kindo_response  # Dynamic response from Kindo AI
    }

# Doctor summary generation route (protected)
@router.post("/generate-summary", summary="Generate Summary", description="Generates a doctor summary based on symptoms")
def generate_summary(symptom_input: str, current_user: dict = Depends(get_current_user)):
    """
    Generates a doctor summary using LlamaIndex and Kindo's AI based on the user's input and historical data.
    """
    user_id = current_user["id"]
    
    # Retrieve user-provided symptoms from the API input
    current_input = symptom_input.current_symptoms  # Get the user-provided symptoms
    
    # Query historical data based on the current input
    historical_data = query_index(user_id, current_input)  # Dynamic query based on user input
    
    # Combine the current input with historical data for the Kindo API
    combined_input = f"{current_input}\nHistorical data: {historical_data}"
    
    # Call Kindo API to generate the summary
    kindo_response = call_kindo_api(combined_input)
    
    return {"summary": kindo_response}