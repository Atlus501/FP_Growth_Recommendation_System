class User(BaseModel):
    username : str
    password : str
    banned : bool = False
    time_preference : "3 months"