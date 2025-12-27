# This file definitely is a top priority for cleaning up and optimizing
from router.misc import generate_random_string
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, FastAPI, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os, base64
from typing import Any, List
from dotenv import load_dotenv
from .auth import auth, build, HttpError, checkPassword, db, PasswordSubmission
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import json, datetime, asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address
from contextlib import asynccontextmanager
# gather credentials and initialize firestore ##
_=load_dotenv('.env')

#############################################################################################

EmailRouter = APIRouter()
limiter = Limiter(key_func=get_remote_address)



class EmailSubmitRequest(BaseModel):
    content:str

#############################################################################################

@EmailRouter.post("/emails")
def getEmails(passwordSubmission:PasswordSubmission = PasswordSubmission(password='')):
    """Checks password and if correct returns the emailing list from Firestore"""
    
    if not checkPassword(passwordSubmission.password):
        raise HTTPException(status_code=401, detail='Password Incorrect')

    return Response(status_code=200,content=json.dumps({'message':'Success','emails':['testData','testData2']}), headers={'Content-Type':'application/json'})

#############################################################################################

@EmailRouter.post("/emails/submit")
@limiter.limit("5/minute")
async def submitEmail(emailRaw:EmailSubmitRequest,request:Request):
    # I need new sets of creds for all my email stuff. Probably the best thing to do for long-term support 

    # Get Creds from auth.py
    creds = auth()
    try:
    # Call the Gmail API
        service:Any = build("gmail", "v1", credentials=creds,cache_discovery=False)

    except HttpError as e:
        raise HTTPException(e.status_code, e.error_details)
    

    # edge cases where email should fail
    if emailRaw.content == "":
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        name:str = emailRaw.content.split('@')[0]
        email:str = emailRaw.content
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')
   
    
    # Check if email is already in table and configure a hashkey accordingly
    identicalQuery:List[Any] = db.table("emails").select("*").eq("username",emailRaw.content).execute().data
    
    random_id:str = generate_random_string(5)
    hash_id:int = hash(tuple([email,random_id]))
    if len(identicalQuery) > 0: # will only ever be 0 or 1 because name is set as primary key
        if identicalQuery[0].get('verified'):
            raise HTTPException(status_code=400, detail='Email already on emailing list')
        else: # If not verified we can send an email again
            random_id = identicalQuery[0].get('random_id')
            hash_id = hash(tuple([email,random_id]))
    else: 
        db.table("emails").upsert({"name":email, "random_id":random_id, "verified":False})



            

    link = f'api.mechmania.ca/verify?ID={hash_id}'

    html = f"""
        Hi There {name}! Thanks for taking an interest in MechMania! To verify that you own this email and proceed, please click the following link: <br>
        <a href="{link}">{f'mechmania.ca/verify/{hash_id}'}</a> <br> <br>

        If this was not you, you can safely ignore this email.<br> <br>
        Thanks,<br>
        Mechmania Team.<br> <br>
        <i>Please do not reply to this email</i>
        <br>
        <br>
        <img src='cid:logoA1B2C3' />
    """
    email_message = buildEmail(f"{email}","organizers@mechmania.ca","NoReply Register Email",html,'Mechmania Team')
    sendEmail(email_message,service)
    
    #email was sent so must add to supabase
    

    return Response(json.dumps({'status':200,'message':'Success! Check your email.'}), status_code=200, headers={'Content-Type':'application/json'})

#############################################################################################


@EmailRouter.get("/verify")
async def verifyEmail(ID:str=''):
    


    creds = auth()
    try:
    # Call the Gmail API
        service = build("gmail", "v1", credentials=creds,cache_discovery=False)

    except HttpError as e:
        raise HTTPException(e.status_code, e.error_details)
    

    name = "test"



    html = f"""
        Hello {name}!, <br>
You are now a part of the MechMania Emailing list! 
<br><br>
If you are a student or teacher interested in competing, please complete <a href="https://docs.google.com/forms/d/1y7HCRmqyI9NbTK-SGDF0p1iFNeYG5clBJTr6lruMvDE">this form<a/> or have your club representatives submit it to register a team.
<br><br>
    This year, we will be running at The University of Waterloo’s Robohub on May 8, 2026. We typically provide the kits a few months in advance to allow your team time to learn, design and build your robot. If you are familiar with robotics or are a beginner, we can provide help in various ways, including lessons on a requested topic or a quick email explanation. In the coming months, a MechMania information document and this year’s schedule will be shared with you. We will contact you further with more information on kits, preparation, and exact details closer to the date. In the meantime, stay updated on any new developments in the competition by following us on Instagram and YouTube.
<br><br>
    If you have any questions or sponsorships inquiries please emails back through this email thread.
    <br>
    <br>
Best regards,
The MechMania Team
<br><br>
        <img src='cid:logoA1B2C3' />
    """

    email_message = buildEmail(f"{email}","organizers@mechmania.ca","Welcome to Mechmania!",html,'Mechmania Team')
    sendEmail(email_message,service)
    # send new email here
    return RedirectResponse(url=f"https://mechmania.ca/emailLanding?ID={ID}",status_code=307)
 


#############################################################################################
# Utilities
#############################################################################################



def sendEmail(message:MIMEMultipart,service:Any):
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    wrapped_message = {'raw': encoded_message}
    _ = (
        service.users()
        .messages()
        .send(userId="me", body=wrapped_message)
        .execute()
    )

    ...


def buildEmail(To='',From='',Subject='',Content='',Name='', CID='logoA1B2C3'):
    # build email use MIME

    message = MIMEMultipart("related")
    message["Subject"] = Subject
    message["From"] = email.utils.formataddr((Name, From))
    message["To"] = To

    # fallback
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)

    # Plain text fallback
    msg_text = MIMEText("Hi There! This is a testing message meant to show that you have registered your email via our newsletter! If you would like to confirm, please click this link:\nhttps://mechmania.ca", 'plain')
    msg_alternative.attach(msg_text)

    # HTML body with embedded image using cid
    html_content = Content.replace("{{cid}}", CID)
    msg_html = MIMEText(html_content, 'html')
    msg_alternative.attach(msg_html)

    # Attach the image
    with open('public/mechmania.png', 'rb') as img:
        mime_img = MIMEImage(img.read(), name=os.path.basename('public/mechmania.png'))
        mime_img.add_header('Content-ID', f'<{CID}>')  # Important!
        mime_img.add_header('Content-Disposition', 'inline', filename=os.path.basename('public/mechmania.png'))
        message.attach(mime_img)

    return message


