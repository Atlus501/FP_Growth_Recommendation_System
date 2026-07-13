import logging
import datetime, timezone

from fastapi import APIRouter, Request, status, HTTPException, Depends, BackgroundTasks
from pydantic import ValidationError

from typing import Annotated
from services.auth.auth_manager import Auth_Manager
from api.routes.schemas.auth import Login, User, ChangeInfo

from helpers.ratelimiter import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

def log_user_activity(username: str, action: str):
    logger.info(f"{datetime.now(timezone.UTC)}: User {username} has {action}")

def get_auth_manager(req : Request) -> Auth_Manager:
    return req.app.state.auth_manager

"""
Route for logging in users
"""
@limiter.limit("10/minute")
@router.post("/login", status_code=status.HTTP_200_OK)
def login(login_info : Login, 
          background_tasks: BackgroundTasks, 
          auth_manager: Annotated[Auth_Manager, Depends(get_auth_manager)],
          req: Request):
          
    login_res = auth_manager.authenticate_user(login_info.username, login_info.password)
    jwt = auth_manager.create_access_token({"sub" : login_info.username})

    background_tasks.add_task(log_user_activity, login_info.username, "SUCCESSFUL LOGIN")

    return {"access_token" : jwt.access_token,
            "token_type" : jwt.token_type}

"""
Route for creating users
"""
@limiter.limit("3/minute")
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create(user: User, 
           auth_manager: Annotated[Auth_Manager, Depends(get_auth_manager)],
           req: Request):

    create_res = auth_manager.create_user(user)

    if not create_res:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="The account wasn't created successfully",
        )

    return {"detail" : "The account was successfully created"}

"""
Route for changing passwords
"""
@limiter.limit("3/minute")
@router.put("/change_pwd", status_code=status.HTTP_200_OK)
async def change_pwd(change_info : ChangeInfo, 
                     auth_manager: Annotated[Auth_Manager, Depends(get_auth_manager)],
                     req: Request):

    change_res = await auth_manager.change_password(change_info.username,
                                              change_info.oldpassword,
                                              change_info.newpassword)

    if not change_res:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The password failed to change",
        )

    return {"detail" : "The password was succcessfully changed"}