import firebase_admin
from firebase_admin import credentials, firestore


# gather credentials and initialize firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
