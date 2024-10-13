
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
import sqlite3

# Function to retrieve symptom data from SQLite
def retrieve_symptom_data(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT symptom FROM symptoms WHERE user_id = ?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    return [row[0] for row in data]

# Create LlamaIndex based on the user data
def create_index():
    data = retrieve_symptom_data(user_id=1)  # You can pass dynamic user_id
    documents = SimpleDirectoryReader(input_data=data).load_data()
    index = VectorStoreIndex(documents)
    # Save index to disk for querying later
    index.save_to_disk("symptoms_index.json")

# Query the index to retrieve relevant user symptoms
def query_index(user_id):
    # Load the pre-built index
    index = VectorStoreIndex.load_from_disk("symptoms_index.json")
    # Query LlamaIndex with the current symptom or condition
    query = "headache, nausea"  # Can dynamically change based on input
    result = index.query(query)
    return result


# Kindo API integration
def call_kindo_api(combined_input):
    url = "https://kindo-api-endpoint/chat/completions"
    headers = {
        "Authorization": "Bearer YOUR_KINDO_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": combined_input,
        "max_tokens": 500
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Route to generate a doctor summary
@app.get("/generate-summary")
def generate_summary(user_id: int):
    # Query the LlamaIndex to get historical symptoms
    historical_data = query_index(user_id)

    # Combine historical data with the current symptom input (hypothetical)
    current_input = "User reports frequent headaches and nausea."
    combined_input = f"{current_input}\nHistorical data: {historical_data}"

    # Call Kindo's API with the combined input
    kindo_response = call_kindo_api(combined_input)
    
    # Return the summary from Kindo's API response
    return {"summary": kindo_response}
