from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Password hashing and verification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT token utility
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=120)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Kindo API call
def call_kindo_api(combined_input):
    url = "https://kindo-api-endpoint/chat/completions"
    headers = {
        "Authorization": f"Bearer YOUR_KINDO_API_KEY",
        "Content-Type": "application/json"
    }
    payload = {"prompt": combined_input, "max_tokens": 500}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
