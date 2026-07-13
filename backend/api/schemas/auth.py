from pydantic import BaseModel

class User(BaseModel):
    username : str
    password : str
    banned : bool = False
    time_preference : "3 months"

class Login(BaseModel):
    username : str
    password : str

class AuthToken(BaseModel):
    access_token: str
    token_type: str

class ChangeInfo(BaseModel):
    username : str
    oldpassword : str
    newpassword : str