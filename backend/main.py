from fastapi import FastAPI, APIRouter, status
from contextlib import asynccontextmanager
import logging
import uvicorn
from dotenv import load_env
import os

#middlewares
from middleware.secure_headers import SecureResponseMiddlware
from middleware.cors import setup_corsmiddleware

#errors
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

#error handlers
from api.error_handler import duplicatekeyerror_handler, exception_handler, http_exception_handler,
                              validationerror_handler, runtimeerror_handler

#routers
from api.routes.auth import router as auth_router

#dependencies initiallized at beginning
from services.auth.authmanager import Auth_Manager
from infrastructure.databases.neo4j import Neo4j_Manager

#creating dependencies 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup]: Triggered before the server starts accepting requests
    logging.basicConfig(level=logging.INFO, filename="job_post_recommendation_system.log", 
                                               format='%(asctime)s - %(levelname)s - %(message)s')
    app.state.auth_manager = Auth_Manager()
    app.state.neo4j_manager = Neo4j_Manager()

    yield

    logging.warning("shutting off services")

#app
app = FastAPI(
    title="job recommendation backend"
    lifespan=lifespan,
    description="Asynchronous backend service managing text context vector lookups",
    version="1.0.0"
)

#adding cors middlware
setup_corsmiddleware(app)
app.add_middlware(SecureResponseMiddlware)

app.include_router(auth_router, prefix="/auth")

app.add_exception_handler(DuplicateKeyError, duplicatekeyerror_handler)
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(ValidationError, validationerror_handler)
app.add_exception_handler(RuntimeError, runtimeerror_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

"""
Function that initially welcomes the user as the are connected to the endpoint.
"""
@app.get("/", status_code=status.HTTP_200_OK)
async def respond():
    response_body = {
        "response" : "you have been connected",
    }
    return response_body

if __name__ = "__main__":
    logging.info("starting services")
    load_env()

    SERVER_IP = os.getenv("SERVER_IP")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT, reload=True)