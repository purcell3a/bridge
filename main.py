import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# JWT token utility functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# FastAPI app instance
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

# Landing page route (list all endpoints)
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <html>
        <head>
            <title>Bridge</title>
        </head>
        <body>
            <h1>Health Logging App API</h1>
            <p>Welcome to the Health Logging API backend. Below is a list of available endpoints:</p>
            <ul>
                <li><b>POST</b> /create-user - Create a new user</li>
                <li><b>POST</b> /login - Login and get a JWT token</li>
                <li><b>GET</b> /users/me - Get details of the logged-in user</li>
                <li><b>POST</b> /log-symptom - Log a symptom for the logged-in user</li>
                <li><b>GET</b> /generate-summary - Generate a doctor summary for the logged-in user</li>
            </ul>
            <p>For interactive documentation, visit <a href="/docs">/docs</a>.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Create a user route (with password hashing)
@app.post("/create-user")
def create_user(name: str, password: str, email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = get_password_hash(password)

    try:
        cursor.execute("INSERT INTO users (name, password, email) VALUES (?, ?, ?)", (name, hashed_password, email))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

    return {"status": "User created successfully", "name": name, "email": email}

# User login route
@app.post("/login", summary="User Login", response_description="Returns an access token for the user")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This endpoint allows users to log in using their email and password. 

    **Input**:
    - `username`: The email of the user (OAuth2 expects "username", but we use it as the email here).
    - `password`: The user's password.

    **Output**:
    - Returns a JWT access token and the token type ("bearer") if the login is successful.
    - The access token is valid for 120 minutes (or the specified expiration time).

    **Error**:
    - Returns a 401 Unauthorized error if the credentials are incorrect.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find user by email (OAuth2 uses 'username' field for login, but it's the email in our case)
    cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    # If user does not exist or password does not match, return an error
    if user is None or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    # Create JWT token valid for ACCESS_TOKEN_EXPIRE_MINUTES (default is 120 minutes)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user[1]}, expires_delta=access_token_expires)

    # Return the access token and token type as JSON response
    return {"access_token": access_token, "token_type": "bearer"}


# Helper function to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE email = ?", (user_email,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": user[0], "name": user[1], "email": user[2]}

# Protected route for getting user information
@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Symptom logging route (protected)
@app.post("/log-symptom")
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
@app.get("/generate-summary")
def generate_summary(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
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
