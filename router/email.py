from typing import Union
from typing import Annotated
from router.misc import getAndorHTML
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, HTTPException
import os, base64
from dotenv import load_dotenv
from .auth import auth, build, HttpError, checkPassword, db, PasswordSubmission
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils

# gather credentials and initialize firestore ##
load_dotenv('.env')

#############################################################################################

EmailRouter = APIRouter()

class EmailSubmitRequest(BaseModel):
    content:str


#############################################################################################

@EmailRouter.post("/emails")
def getEmails(passwordSubmission:PasswordSubmission = PasswordSubmission(content='')):
    """Checks password and if correct returns the emailing list from Firestore"""
    
    if not checkPassword(passwordSubmission.content):
        raise HTTPException(status_code=401, detail='Password Incorrect')

    documentRef = db.collection('emails').document('emails')

    if documentRef is None:
        raise HTTPException(status_code=500, detail='Database Error 00A. Please notify organizers@mechmania.ca.')
    emails = documentRef.get().to_dict() or {'val':[]}

    return {'emails':emails['val']} 

#############################################################################################

@EmailRouter.post("/emails/submit")
def submitEmail(emailSubmitRequest: EmailSubmitRequest|None = None):
    

    if emailSubmitRequest is None:
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        email = validate_email(emailSubmitRequest.content)[1]
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')

    # Get Creds from auth.py
    creds = auth()

    try:
    # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    
    #
    except HttpError as e:
        raise HTTPException(e.status_code, e.error_details)
    img_data = open('public/mechmania.png', 'rb').read()
    html = f"""
        Hi There! This is a testing message meant to show that you have registered your email via our newsletter! If you would like to confirm, please click this link:<br>
        <a href="{'mechmania.ca'}">{'mechmania.ca'}</a> <br> <br>
        If this was not you, you can safely ignore this email.<br> <br>
        Thanks,<br>
        Mechmania Team.<br> <br>
        <img src='cid:logoA1B2C3' />
    """

    email_message = buildEmail(f"{email}","organizers@mechmania.ca","Automated Newsletter Confirmation",html,'Mechmania Team')
    encoded_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    message = {'raw': encoded_message}
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )
    return {'email':email}

#############################################################################################

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