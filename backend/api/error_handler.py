import logging
from fastapi import Request, status, HTTPException
from fastapi.exception_handlers import http_exception_handler

from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

logger.getLogger(__name__)

"""
Global error handler for HTTP exceptions
"""
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Just let FastAPI handle it normally so 401s, 404s, etc., stay intact
    return await http_exception_handler(request, exc)

"""
Global error handler for duplciate key exceptions
"""
def duplicatekeyerror_handler(request: Request, e: DuplicateKeyError):
    logger.error(f"Duplicate key detected! {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail" : "You have declared a key that already exists. Try another value"}
    )

"""
Global error handler for invalid token errors
"""
def invalidtokenerror_handler(request: Request, e : InvalidTokenError):
    logger.error(f"Invalid token was used! {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail" : "You have used an invalid jwt"}
    )

"""
Global error handler for validation errors
"""
def validationerror_handler(request: Request, e: ValidationError):
    logger.error(f"Invalid datatypes! {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail" : "Invalid datatypes were detected in your request"}
    )

"""
Global error handler for runtime errors
"""
def runtimeerror_handler(request: Request, e : RuntimeError):
    logger.error(f"A runtime error has triggered: {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail" : "A rntime error has triggered"}
    )

"""
Global error handler for miscellaneous, uncategorized errors
"""
def exception_handler(request: Request, e : Exception):
    logger.critical(f"An unexpected error has occured during runtime: {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail" : "There was an unexpected runtime error"}
    )
