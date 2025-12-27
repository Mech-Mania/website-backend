# Part of this code is sampled (just the auth() function) from google's quickstart docs here : https://developers.google.com/workspace/gmail/api/quickstart/python
# For any future devs of this project: If you need the token, either email the previous dev (easier) or get the credentials 
# for the api client on the google workspace, then run those cred through here to get an auth token which is what you use for auth on the main app
# This 

import os.path
from typing import Any, List
from pydantic import BaseModel
from supabase import create_client, Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json, os
from dotenv import load_dotenv


#load environment variables
_=load_dotenv('.env')

# load supabase client
url:str = os.environ.get("SUPABASE_URL") or ""
key:str = os.environ.get("SUPABASE_KEY") or ""


db:Client = create_client(url,key)



#load email client
# If modifying these scopes, delete the file token.json or the token in environment
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GMAIL_SERVICE_ACCOUNT_KEY = json.loads(os.environ.get('GMAIL_SERVICE_ACCOUNT_KEY') or '{}')

def auth():
  # TODO set token to loaded creds from DB
  """Runs to grab cred to do executive actions"""
  creds = None
  db_data:List[Any] = db.table("tokens").select("value").eq("name","GMAIL_SERVICE_CREDS").execute().data
  try:               Token = db_data[0].get('value')
  except IndexError: Token = None

  if Token:
    print(Token)
    creds = Credentials.from_authorized_user_info(json.loads(Token),SCOPES)

  # If there are no (valid) credentials available, let the user log in.

  if not creds or not creds.valid:

    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())

    else:
      flow = InstalledAppFlow.from_client_config(GMAIL_SERVICE_ACCOUNT_KEY,SCOPES)
      creds = flow.run_local_server(port=62800, access_type='offline', include_granted_scopes=False)
    # Save the credentials for the next run
    response = (
        db.table("tokens")
        .upsert({"name":"GMAIL_SERVICE_CREDS", "value": creds.to_json()})
        .execute()
    )
     
    
  return creds


class PasswordSubmission(BaseModel):
    password:str

def checkPassword(password:str):
  return password == os.environ.get('ADMIN_PASSWORD')

