# This code is from google's quickstart docs here: https://developers.google.com/workspace/gmail/api/quickstart/python
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

def auth():
  """Runs to grab cred to do executive actions"""
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.


  if not creds or not creds.valid:

    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

    else:
      flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
      creds = flow.run_local_server(port=62800)
    # Save the credentials for the next run


    with open("token.json", "w") as token:
      token.write(creds.to_json())
  
  return creds

if __name__ == "__main__":
  auth()


class PasswordSubmission(BaseModel):
    content:str

def checkPassword(password:str):
  return password == os.environ.get('ADMIN_PASSWORD')

