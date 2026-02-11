from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.model.user import UserCreate, UserInDB, Token
from app.model.readers import Reader
from app.model.author import Author
from app.crud.user import create_user, find_user_by_username
from app.crud.readers import create_reader
from app.crud.authors import create_author
from app.auth_utils import hash_password, verify_password, create_access_token, decode_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token : str = Depends(oauth2_scheme)):
    """
    This is a DEPENDENCY. Any route that includes 'Depends(get_current_user)'
    will automatically require a valid JWT.
    
    How it works:
    1. FastAPI sees Depends(get_current_user) on a route.
    2. It calls this function BEFORE the route handler.
    3. This function extracts the token from the Authorization header.
    4. It decodes the token and returns the user data.
    5. If the token is invalid, it raises a 401 error and the route handler never runs.
    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The payload contains the claims we put in when creating the token
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    return payload  # Returns {"sub": "nabil", "roles": ["reader", "author"], "exp": ...}



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    #1. Check if user already exists
    existing = await find_user_by_username(user.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    hashed = hash_password(user.password)

    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed,
        roles=user.roles)

    # Save User to MongoDB
    user_id = await create_user(user_in_db)

    # Auto-create a Reader profile for every user
    reader_profile = Reader(
        name=user.username,
        favorites=[],
        in_progress=[],
        finished=[],
        user_id=user.username
    )
    await create_reader(reader_profile)

    # If the user registered as an author, also create an Author profile
    if "author" in user.roles:
        author_profile = Author(
            name=user.username,
            biography=None,
            book_list=[],
            profile_picture=None,
            user_id=user.username
        )
        await create_author(author_profile)

    return {"id": user_id, "status": "registered"}

@router.post("/login", response_model = Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2PasswordRequestForm expects form fields: 'username' and 'password'.
    This is a standard that Swagger UI knows how to work with automatically.
    """
    user = await find_user_by_username(form_data.username)
    if not user: 
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
        detail="Incorrect username or password")
    
    #2. Check the password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password")

    #3. Create the JWT with the user's info embedded
    access_token = create_access_token(data={"sub": user["username"], "roles": user["roles"]})

    #4. Return the token
    return Token(access_token=access_token, token_type="bearer")


