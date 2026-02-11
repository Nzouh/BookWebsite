
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

# Password Hashing

#CryptContext from passlib knows how to hash and verify passwords.
# bcrypt is the algorithm, it is slow on purpose for brute force attacks to be difficult.ArithmeticError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password : str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



#Now that we can hash and verify the password, let's create JWT tokens
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data : dict) -> str:
    """
    Creates a JWT from a dictionary of data (called "claims").
    
    Example input:  {"sub": "nabil", "roles": ["reader", "author"]}
    Example output: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWJpbCIs..."
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp" : expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token : str) -> dict | None:
    """
    Takes a JWT string and returns the data inside it.
    Returns None if the token is invalid or expired.
    """

    try:
        # jwt.decode() verifies the signature and checks expiration automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        # This catches expired tokens, tampered tokens, etc.
        return None