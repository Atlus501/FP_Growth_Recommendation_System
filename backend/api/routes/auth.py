import logging
import datetime, timezone
import uuid

from fastapi import APIRouter, Request, status, HTTPException, Depends, BackgroundTasks, Response
from pydantic import ValidationError

from typing import Annotated
from services.auth_service import Auth_Service
from infrastructure.jwt import Jwt_Manager

from schemas.request_body.auth import Login, User, ChangeInfo

from helpers.ratelimiter import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

def log_user_activity(username: str, action: str):
    logger.info(f"{datetime.now(timezone.UTC)}: User {username} has {action}")

def get_auth_service(req : Request) -> Auth_Service:
    return req.app.state.Auth_Service

def get_jwt_manager(req : Request) -> Jwt_Manager:
    return req.app.state.jwt_manager

"""
Route for logging in users
"""
@limiter.limit("10/minute")
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login_info : Login, 
                background_tasks: BackgroundTasks, 
                Auth_Service: Annotated[Auth_Service, Depends(get_auth_service)],
                req: Request,
                res: Response):
          
    login_res = await Auth_Service.authenticate_user(login_info.username, login_info.password)
    jwt = jwt_manager.create_access_token({"sub" : login_info.username})

    background_tasks.add_task(log_user_activity, login_info.username, "SUCCESSFUL LOGIN")

    res.set_cookie(key="access_token",
                   value=str(jwt.access_token),
                   samesite="Strict",
                   secure=True,
                   httponly=True,
                   max_age=1800)

    user_uuid = uuid.uuid4()
    await Auth_Service.set_uuid(login_info.username, user_uuid)

    res.set_cookie(key="refresh_token",
                   value=str(user_uuid),
                   samesite="Strict",
                   secure=True,
                   httponly=True,
                   max_age=604800)

    return {"detail" : "users successfully authenticated"}

"""
Route for refreashing tokens
"""
@limiter.limit("3/minute")
@router.get("/refresh", status_code=status.HTTP_200_OK)
async def refreash_token(
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
    Auth_Service: Annotated[Auth_Service, Depends(get_auth_service)],
    jwt_manager: Annotated[Jwt_Manager, Depends(get_jwt_manager)],
    res: Response,
):

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie is missing."
        )

    confirmed = await Auth_Service.confirm_uuid(refresh_token)
    if not confirmed:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="This is an invalid refresh token"
        )

    jwt = jwt_manager.create_access_token({"sub" : confirmed['username']})

    res.set_cookie(key="access_token",
                    value=str(jwt.access_token),
                    samesite="Strict",
                    secure=True,
                    httponly=True,
                    max_age=1800)

    return {"detail" : "successfully refreshed token"}

"""
Route for creating users
"""
@limiter.limit("3/minute")
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create(user: User, 
                Auth_Service: Annotated[Auth_Service, Depends(get_auth_service)],
                req: Request):

    create_res = await Auth_Service.create_user(user)

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
                     Auth_Service: Annotated[Auth_Service, Depends(get_auth_service)],
                     req: Request):

    change_res = await Auth_Service.change_password(change_info.username,
                                              change_info.oldpassword,
                                              change_info.newpassword)

    if not change_res:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The password failed to change",
        )

    return {"detail" : "The password was succcessfully changed"}