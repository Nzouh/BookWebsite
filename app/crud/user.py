from pydantic import BaseModel
from typing import Optional


#The info the user sends
class User(BaseModel):
    username : str
    email: str
    password : str #This string will be hashed before saving
    roles : list["reader"] # Default role


#What we store in MongoDB
class UserInDB(BaseModel):
    username : str
    email : str
    hashed_password: str
    roles : list["reader"]

#What we return to the client, the client will use this to 
class Token(BaseModel):
    access_token : str
    token_type : str # always is "Bearer"
