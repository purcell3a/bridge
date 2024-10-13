import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.auth import login, get_current_user
from app.users import create_user
from app.symptoms import log_symptom, generate_summary
from database.database import get_db_connection
from app.utils import call_kindo_api

# Import routers from your modules

app = FastAPI()

# Include routers
origins = [
"https://bridge-fe-8aeb1e1bce30.herokuapp.com/"
"http://localhost:3000"
# "https://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Change to ["*"] to allow all origins
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

from app.auth import router as auth_router
from app.symptoms import router as symptoms_router
from app.users import router as user_router
app.include_router(auth_router, prefix="/auth")
app.include_router(symptoms_router, prefix="/symptoms")
app.include_router(user_router, prefix="/users")
# app.include_router(utils_router,prefox="/utils")

# Landing page route (list all endpoints)
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <html>
        <head>
            <title>Bridge</title>
        </head>
        <body>
            <h1>Bridge</h1>
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
