from typing import Union
from enum import Enum
from typing import Annotated
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, HTTPException, Header

EmailRouter = APIRouter()


class EmailSubmitRequest(BaseModel):
    email:str


@EmailRouter.post("/emails/submit")
def submit_email(email_submit_request: EmailSubmitRequest|None = None):
    
    if email_submit_request is None:
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        email = validate_email(email_submit_request.email)[1]
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')


    return {'email':email}