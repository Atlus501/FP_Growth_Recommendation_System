from fastapi import HTTPException
from pwdlib import PasswordHash

from config.settings import settings

from schemas.services.auth import User

from infrastructure.databases.mongodb.users import User_DB

"""
This is the class that will manage the authentication information & jwt of users
"""
class Auth_Service:
    """
    Constructor for the Auth_Manager
    Params: database (User_DB)
    """
    def __init__ (self, database : User_DB):
        self.password_hash = PasswordHash.recommended()
        self.collection = database.collection

    """
    Function that creates users and stores them in the database
    Params: user (User) 
    """
    async def create_user(self, user : User):
        user_data = user.model_dump()
        user_object['password'] = self.hash_password(user.password)
        user = await self.collection.insert_one(user_object)
        return str(user.inserted_id)

    """
    Function that gets users
    Params: username (str)
    Returns: result of whether they can find an entry with that username
    """
    async def get_user(self, username : str):
        return await self.collection.find_one({"username" : username})

    """
    Function that sets uuids
    Params: username (str)
            uuid (uuid)
    Returns: result of whether the uuid has been updated
    """
    async def set_uuid(self, username : str, uuid : uuid):
        return await self.collection.update_one({"username" : username}, {"$set" : {"uuid" : uuid}})

    """
    Function that confirms a user's uuid
    Params: username (str)
            uuid (uuid)
    """
    async def confirm_uuid(self, uuid : str):
        return await self.collection.find_one({"uuid" : uuid})

    """
    Function that gets users
    Params: username (str)
            old_password (str)
            new_password (str)
    """
    async def change_password(self, username : str, old_password: str, new_passowrd: str):
        user = await self.collection.find_one({"username" : username})

        if not user or not self.verify_password(old_password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Received incorrect information",
            )

        hashed_new_password = self.hash_password(new_password)

        query_filter = {'username' : username}
        update_operation = { '$set' : 
            { 'password' : hashed_new_password }
        }

        return await self.collection.update_one(query_filter, update_operation)

    """
    Function that hashes the password
    Params: password (str)
    """
    def hash_password(self, password):
        return self.password_hash.hash(password)

    """
    Function that verifies the passwords 
    Params: plain_password (str) -- unhashed password
            hashed_password (str) -- hashed version of the password
    Returns: boolean of whether the passwords match
    """
    def verify_password(self, plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    """
    Function that authenticates users
    Params: username (str)
            password (str)
    Returns: user object
    """
    async def authenticate_user(self, username: str, password: str):
        user = await self.get_user(username)
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
