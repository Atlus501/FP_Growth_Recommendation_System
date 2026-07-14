from pydantic import BaseModel

class Get_Job_Request(BaseModel):
    access_token : str