from fastapi import APIRouter, HTTPException
from database.database import get_db_connection
from app.utils import get_password_hash

# Create the router
router = APIRouter()

@router.post("/create-user", summary="Create User", description="Create a new user with a hashed password")
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
