from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.auth import login_for_access_token, get_current_user
from app.users import create_user
from app.symptoms import log_symptom, generate_summary
from database.database import get_db_connection


app = FastAPI()

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
