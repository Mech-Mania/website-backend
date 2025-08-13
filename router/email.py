from router.misc import getAndorHTML, generate_random_string
from pydantic import BaseModel, validate_email
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os, base64
from google.cloud import firestore
from dotenv import load_dotenv
from .auth import auth, build, HttpError, checkPassword, db, PasswordSubmission
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.utils
import json, datetime, asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address

# gather credentials and initialize firestore ##
load_dotenv('.env')

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

    documentRef = db.collection('emails').document('emails')

    if documentRef is None:
        raise HTTPException(status_code=500, detail='Database Error 00A. Please notify organizers@mechmania.ca.')
    emails = documentRef.get().to_dict() or {'val':[]}

    return Response(status_code=200,content=json.dumps({'message':'Success','emails':emails['val']}), headers={'Content-Type':'application/json'})

#############################################################################################

@EmailRouter.post("/emails/submit")
@limiter.limit("5/minute")
async def submitEmail(request:Request):
    
    req = (await request.json())
    if req['content'] is None:
        raise HTTPException(status_code=400, detail='No email provided')
    
    try:
        name, email = req['content'].split('@')
    except:
        raise HTTPException(status_code=400, detail='Invalid email format')
    # Get Creds from auth.py
    creds = auth()
    prevList = db.collection('emails').document('emails').get().to_dict() or {}

    if email in prevList['val']:
        return Response(json.dumps({'status':400,'message':'Your email is already in our emailing list!'}), status_code=200, headers={'Content-Type':'application/json'})

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
        service = build("gmail", "v1", credentials=creds,cache_discovery=False)

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
    print('made it to here 2')
    email_message = buildEmail(f"{email}","organizers@mechmania.ca","NoReply Register Email",html,'Mechmania Team')
    encoded_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    message = {'raw': encoded_message}
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )
    print('made it to here 3')
    return Response(json.dumps({'status':200,'message':'Success! Check your email.'}), status_code=200, headers={'Content-Type':'application/json'})

#############################################################################################


@EmailRouter.get("/verify")
async def verifyEmail(ID:str=''):
    creds = auth()
    if len(ID) != 128:
        return HTMLResponse(content=getAndorHTML(),status_code=422)
    
    storedIDs = db.collection('emails').document('validationRequired').get().to_dict() or {}

    if ID not in storedIDs.keys():
        return RedirectResponse(url="https://mechmania.ca/emailLanding?ID={ID}",status_code=307)
    
    email = storedIDs[ID]['email']

    @firestore.transactional
    def runTransaction(transaction):

        docRef = db.collection('emails').document('emails')
        prevList = docRef.get(transaction=transaction).to_dict() or {}

        if email in prevList['val']:
            return {'end':True, 'redir':RedirectResponse(url=f"https://mechmania.ca/emailLanding?ID={ID}",status_code=307)}
        
        transaction.update(docRef,{'val':[email]+prevList['val']})
        return {'end':False, 'redir':RedirectResponse(url=f"https://mechmania.ca/emailLanding?ID={ID}",status_code=307)}
    
    response = runTransaction(db.transaction())
    if response['end']:
        return response['redir']


    name,email = validate_email(email)

    try:
    # Call the Gmail API
        service = build("gmail", "v1", credentials=creds,cache_discovery=False)

    except HttpError as e:
        raise HTTPException(e.status_code, e.error_details)
    
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
    encoded_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
    message = {'raw': encoded_message}
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )




    # send new email here


    return RedirectResponse(url=f"https://mechmania.ca/emailLanding?ID={ID}",status_code=307)
 


@EmailRouter.get("/checkID")
async def verifyID(ID:str=''):
    
    storedIDs = db.collection('emails').document('validationRequired').get().to_dict() or {}
    if ID not in storedIDs.keys():
        return Response(status_code=200,content=json.dumps({'verified':False}))
    
    return Response(status_code=200,content=json.dumps({'verified':True}))
    

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


async def rollingTempPurge():
    
    temp = [i for i in range(24)]
    @firestore.transactional
    def runTransaction(transaction):
        docRef = db.collection('emails').document('validationRequired')
        snapshot = docRef.get(transaction=transaction).to_dict() or {}
        for tempData in [x for x in snapshot.keys()]:
            if temp[datetime.datetime.now().hour-2] > int(snapshot[tempData]['time']):
                del snapshot[tempData]
            elif int(snapshot[tempData]['time']) > datetime.datetime.now().hour:
                del snapshot[tempData]
        transaction.set(docRef,snapshot)

    runTransaction(db.transaction())
    while True:
        await asyncio.sleep(7200)
        runTransaction(db.transaction())
        

@EmailRouter.on_event('startup')
def runstuff():
    asyncio.create_task(rollingTempPurge())

