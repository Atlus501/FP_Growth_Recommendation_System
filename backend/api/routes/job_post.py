from fastapi import APIRouter, status, Request, depends
from typing import Annotated

from helpers.ratelimiter import limiter

from schemas.request_body import Get_Job_Request

from infrastructure.jwt import Jwt_Manager

from services.job_post import Job_Post_Service

router = APIRouter()

def get_jwt_manager(req : Request) -> Jwt_Manager:
    return req.app.state.jwt_manager

def get_job_post_service(req : Request) -> Job_Post_Service:
    return req.app.state.job_post_service

@limit.limit("10/minute")
@router.get("/")
async def get_job_posts(
    access_token : Annotated([str | None : Cookie(alias="access_token")]),
    job_post_service : Annotated([Job_Post_Service : Depends(get_job_post_service)]),
    jwt_manager : Annotated([Jwt_Manager : Depends(get_jwt_manager)])
):

    current_user = await jwt_manager.get_current_user(content.access_token)
    
