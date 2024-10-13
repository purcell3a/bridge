import os
import sqlite3
import requests
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# Load environment variables from .env file
load_dotenv()

# Retrieve the Kindo API key from environment
KINDO_API_KEY = os.getenv("KINDO_API_KEY")

# Function to retrieve symptom data from SQLite
def retrieve_symptom_data(user_id):
    conn = sqlite3.connect('database.db')  # Or use DATABASE_URL if you prefer
    cursor = conn.cursor()
    cursor.execute("SELECT symptom FROM symptoms WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return [row[0] for row in data]

# Create LlamaIndex based on the user data
def create_index(user_id):
    data = retrieve_symptom_data(user_id)
    documents = SimpleDirectoryReader(input_data=data).load_data()
    index = VectorStoreIndex(documents)
    # Save index to disk for querying later
    index.save_to_disk(f"symptoms_index_{user_id}.json")

# Query the index to retrieve relevant user symptoms
def query_index(user_id, current_symptoms: str):
    """
    Query the LlamaIndex to retrieve relevant user symptoms based on current input.
    
    Args:
        user_id (int): The ID of the user.
        current_symptoms (str): The symptoms or input from the user to adjust the query.

    Returns:
        result: The result of the LlamaIndex query based on the user's input.
    """
    # Load the pre-built index for this user
    index = VectorStoreIndex.load_from_disk(f"symptoms_index_{user_id}.json")
    
    # Use the user's current symptoms as the query
    query = current_symptoms  # This dynamically sets the query based on the user's input
    
    # Query the index using the current symptoms
    result = index.query(query)
    
    return result


# Kindo API integration
def call_kindo_api(user_input: str):
    """
    Call Kindo API with the provided user input and return the response.
    """
    if not KINDO_API_KEY:
        raise ValueError("KINDO_API_KEY is not set in the environment variables")
    
    url = "https://llm.kindo.ai/v1/chat/completions"  # Kindo API endpoint
    headers = {
        "api-key": KINDO_API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "model": KINDO_MODEL_NAME,  # Specify the model name
        "messages": [
            {"role": "user", "content": user_input}  # Send the symptom as user input
        ],
        "max_tokens": 150  # Limit the response length (you can adjust this)
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises an error for any non-2xx response
    
    # Parse the response and extract the message
    kindo_response = response.json()
    return kindo_response["choices"][0]["message"]["content"]  # Adjust based on response format
