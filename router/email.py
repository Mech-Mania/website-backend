from router.misc import getAndorHTML, generate_random_string
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os, base64
from dotenv import load_dotenv
from .auth import auth, build, HttpError, checkPassword, db, PasswordSubmission
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import json, datetime

# gather credentials and initialize firestore ##
load_dotenv('.env')

#############################################################################################

EmailRouter = APIRouter()

class EmailSubmitRequest(BaseModel):
    content:str


#############################################################################################

@EmailRouter.post("/emails")
def getEmails(passwordSubmission:PasswordSubmission = PasswordSubmission(password='')):
    """Checks password and if correct returns the emailing list from Firestore"""
    
    if not checkPassword(passwordSubmission.password):
        raise HTTPException(status_code=401, detail='Password Incorrect')

    documentRef = db.collection('emails').document('emails')

    if documentRef is None:
        raise HTTPException(status_code=500, detail='Database Error 00A. Please notify organizers@mechmania.ca.')
    emails = documentRef.get().to_dict() or {'val':[]}

    return Response(status_code=200,content=json.dumps({'message':'Success','emails':emails['val']}), headers={'Content-Type':'application/json'})

#############################################################################################

@EmailRouter.post("/emails/submit")
async def submitEmail(request:Request):
    
    req = (await request.json())
    if req['content'] is None:
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        name, email = validate_email(req['content'])
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')

    # Get Creds from auth.py
    creds = auth()

    storedIDs = db.collection('emails').document('validationRequired').get().to_dict() or {}

    time = datetime.datetime.now().hour
    key = generate_random_string(128)

    while key in storedIDs.keys():
        key = generate_random_string(128)
    
    data = {
        "time":time,
        "email":email
    }
    db.collection('emails').document('validationRequired').update({key:data})
    link = f'api.mechmania.ca/verify?ID={key}'

    try:
    # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as e:
        raise HTTPException(e.status_code, e.error_details)
    
    html = f"""
        Hi There {name}! Thanks for taking an interest in MechMania! To verify that you own this email and proceed, please click the following link: <br>
        <a href="{link}">{f'mechmania.ca/verify/{key}'}</a> <br> <br>

        If this was not you, you can safely ignore this email.<br> <br>
        Thanks,<br>
        Mechmania Team.<br> <br>
        <i>Please do not reply to this email</i>
        <br>
        <br>
        <img src='cid:logoA1B2C3' />
    """

    email_message = buildEmail(f"{email}","organizers@mechmania.ca","NoReply Register Email",html,'Mechmania Team')
    encoded_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    message = {'raw': encoded_message}
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )
    
    return Response(json.dumps({'message':'Success, check your email.'}), status_code=200, headers={'Content-Type':'application/json'})

#############################################################################################
# from starlette.status import HT
@EmailRouter.get("/verify")
async def verifyEmail(ID:str=''):
    print(len(ID), ID)
    if len(ID) != 128:
        return HTMLResponse(content=getAndorHTML(),status_code=422)
    
    storedIDs = db.collection('emails').document('validationRequired').get().to_dict() or {}

    if ID not in storedIDs.keys():
        return RedirectResponse(url="https://mechmania.ca/invalidKey",status_code=307)
    
    email = storedIDs[ID]['email']

    # maybe run some of this in a transaction
    prevList = db.collection('emails').document('testemails').get().to_dict() or {}
    if email in prevList:
        return RedirectResponse(url=f"https://mechmania.ca/valid?ID={ID}",status_code=307) # add something for if previously existing
    
    db.collection('emails').document('testemails').update({'val':[email]+prevList['val']})


    # send new email here


    return RedirectResponse(url=f"https://mechmania.ca/valid?ID={ID}",status_code=307)

    

    

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

#############################################################################################


