# Bridge

This is a health logging app built with FastAPI that allows users to log symptoms, view historical data, and generate summaries for healthcare professionals using the Kindo API. The project utilizes SQLite for local data storage and LlamaIndex for symptom analysis.
Features

    User Management: Create and retrieve users.
    Symptom Logging: Users can log their symptoms, and the data is stored in an SQLite database.
    Historical Data Summary: The app uses LlamaIndex to analyze user symptoms and generate historical summaries.
    Kindo AI Integration: Generates a doctor summary using the Kindo AI API for healthcare professionals.

## Requirements

    Python 3.10+
    Pipenv for dependency management
    SQLite for local database
    Uvicorn for running FastAPI
    Heroku CLI (for deployment)

# Local Development Setup

## Step 1: Clone the Repository
`git clone https://github.com/your-username/your-repo-name.git`

## Step 2: Set Up Environment
Use Pipenv for managing dependencies.
`pipenv install`

Activate Vitual Enviornment
`pipenv shell`

## Step 3: Create a .env File
Create a .env file in the project root directory to store your environment variables:
`touch .env`

## Step 4: Initialize the SQLite Database
Make sure your database schema is set up. Run the following command to initialize your SQLite database
`python3 models.py`

## Step 5: Run the Application
Use uvicorn to run the FastAPI app locally:
`uvicorn main:app --reload`

# API Endpoints
## User Management

    Create User: POST /create-user
        Body: { "name": "John", "email": "john@example.com" }
        Response: { "status": "User created successfully", "name": "John", "email": "john@example.com" }
    Get User: GET /get-user/{user_id}
        Response: { "id": 1, "name": "John", "email": "john@example.com" }

##  Symptom Logging

    Log Symptom: POST /log-symptom
        Body: { "symptom": "headache", "user_id": 1 }
        Response: { "status": "Symptom logged successfully" }

##  Doctor Summary

    Generate Summary: GET /generate-summary
        Response: { "summary": "Generated summary from Kindo API" }

