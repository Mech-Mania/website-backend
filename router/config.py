import firebase_admin
from firebase_admin import credentials, firestore
import dotenv
import json

# gather credentials and initialize firestore
KeyString:str = dotenv.get_key(dotenv_path='.env', key_to_get='FIREBASE_SERVICE_ACCOUNT_KEY') or ''
cred = credentials.Certificate(json.JSONDecoder().decode(KeyString))
firebase_admin.initialize_app(cred)

db = firestore.client()
