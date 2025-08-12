from typing import Union
from typing import Annotated
from router.misc import getAndorHTML
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, HTTPException, Header
from .config import db
import os
from dotenv import load_dotenv

# gather credentials and initialize firestore ##
load_dotenv('.env')

# # just to figure out what http is for
# from starlette.status import HTTP_405_METHOD_NOT_ALLOWED


Password = os.environ.get('ADMIN_PASSWORD')
EmailRouter = APIRouter()

class EmailSubmitRequest(BaseModel):
    content:str

class PasswordSubmission(BaseModel):
    content:str

@EmailRouter.post("/emails/submit")
def submit_email(emailSubmitRequest: EmailSubmitRequest|None = None):
    
    if emailSubmitRequest is None:
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        email = validate_email(emailSubmitRequest.content)[1]
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')


    return {'email':email}



@EmailRouter.post("/emails")
def get_emails(passwordSubmission:PasswordSubmission = PasswordSubmission(content='')):
    """Checks password and if correct returns the emailing list from Firestore"""
    
    if passwordSubmission.content != Password:
        raise HTTPException(status_code=401, detail='Password Incorrect')

    documentRef = db.collection('emails').document('emails')

    if documentRef is None:
        raise HTTPException(status_code=500, detail='Database Error 00A. Please notify organizers@mechmania.ca.')
    emails = documentRef.get().to_dict() or {'val':[]}

    return {'emails':emails['val']} 

