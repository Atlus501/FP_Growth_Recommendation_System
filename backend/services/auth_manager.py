from typing import Annotated
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from api.schemas.auth import AuthToken, User
from config.settings import settings

"""
This is the class that will manage the authentication information & jwt of users
"""
class Auth_Manager:
    """
    Constructor for the Auth_Manager
    """
    def __init__ (self, database : User_Manager):
        self.password_hash = PasswordHash.recommended()
        self.db = database
        self.hash_function = settings.HASH_ALGORITHM
        self.secret_key = settings.SECRET_KEY


    """
    Function that creates users and stores them in the database
    """
    def create_user(self, user : User):
        user_collection = self.db.get_collection("users")
        user_data = user.model_dump()
        user_object['password'] = self.hash_password(user.password)
        user = user_collection.insert_one(user_object)
        return str(user.inserted_id)

    """
    Function that gets users
    """
    def get_user(self, username : str):
        user_collection = self.db.get_collection("users")
        user = user_collection.find_one({"username" : username})
        return user

    """
    Function that gets users
    """
    async def change_password(self, username : str, old_password: str, new_passowrd: str):
        user_collection = self.db.get_collection("users")
        user = await user_collection.find_one({"username" : username})

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

        user = await user_collection.update_one(query_filter, update_operation)
        return user

    """
    Function that hashes the password
    """
    def hash_password(self, password):
        return self.password_hash.hash(password)

    """
    Function that verifies the passwords 
    Params: plain_password (str) -- unhashed password
            hashed_password (str) -- hashed version of the password
    Returns: boolean of whether the passwords match
    """
    def verify_password(plain_password, hashed_password):
        return self.password_hash.verify(plain_password, hashed_password)

    """
    Function that creates the jwt for the user
    Params: data (dict) -- data of access token attributes like username
            expires_delta -- ttl of data token
    Returns: an encoded jwt
    """
    def create_access_token(data: dict, duration=60*12):
        expires_delta = timedelta(minutes=duration)

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.hash_function)
        return AuthToken(access_token=encoded_jwt, token_type="bearer")

    """
    Function for decoding jwts
    Params: token ()
    Returns: user object that contains user information
    """
    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.hash_function])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        user = get_user(fake_users_db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    """
    Function that authenticates users
    Params: username (str)
            password (str)
    Returns: user object
    """
    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return True
