# Part of this code is sampled (just the auth() function) from google's quickstart docs here : https://developers.google.com/workspace/gmail/api/quickstart/python
# For any future devs of this project: If you need the token, either email the previous dev (easier) or get the credentials 
# for the api client on the google workspace, then run those cred through here to get an auth token which is what you use for auth on the main app
# This 

import os.path
from typing import Any
from pydantic import BaseModel
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.cloud.firestore
import json, os
from dotenv import load_dotenv



#load firestore
load_dotenv('.env')
KeyString:str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY') or '{}'
db = google.cloud.firestore.Client.from_service_account_info(json.loads(KeyString))
#load email client
# If modifying these scopes, delete the file token.json or the token in environment
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GMAIL_SERVICE_ACCOUNT_KEY = json.loads(os.environ.get('GMAIL_SERVICE_ACCOUNT_KEY') or '{}')


def auth():
  load = db.collection('Auth').document('Tokens').get(['Gmail_API']).to_dict() or {}
  TOKEN = load["Gmail_API"]
  """Runs to grab cred to do executive actions"""
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if TOKEN:
    creds = Credentials.from_authorized_user_info(json.loads(TOKEN),SCOPES)

  # If there are no (valid) credentials available, let the user log in.


  if not creds or not creds.valid:

    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

    else:
      flow = InstalledAppFlow.from_client_config(GMAIL_SERVICE_ACCOUNT_KEY,SCOPES)
      creds = flow.run_local_server(port=62800, access_type='offline', include_granted_scopes=False)
    # Save the credentials for the next run

    db.collection('Auth').document('Tokens').update({'Gmail_API':creds.to_json()})
  
  return creds


class PasswordSubmission(BaseModel):
    password:str

def checkPassword(password:str):
  return password == os.environ.get('ADMIN_PASSWORD')

