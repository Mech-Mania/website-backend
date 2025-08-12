import firebase_admin
from firebase_admin import credentials, firestore
import json, os
from dotenv import load_dotenv

# gather credentials and initialize firestore ##
load_dotenv('.env')
KeyString:str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY') or '{}'
print(KeyString)
cred = credentials.Certificate(json.loads(KeyString))
firebase_admin.initialize_app(cred)

db = firestore.client()
