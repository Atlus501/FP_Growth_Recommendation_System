from pydantic import BaseModel

class User(BaseModel):
    username : str
    password : str
    banned : bool = False
    time_preference : str = "3 months"

class Login(BaseModel):
    username : str
    password : str

class ChangeInfo(BaseModel):
    username : str
    oldpassword : str
    newpassword : str