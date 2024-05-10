import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH = os.getenv("FIRESTORE_SERVICE_ACCOUNT_PATH")

def create_firestore_client() -> firestore.Client:
    firebase_credentials = credentials.Certificate(FIRESTORE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(firebase_credentials)

    return firestore.client()

def firestore_test():
    db = create_firestore_client()

    doc_ref = db.collection('holdings-data').document('05092024')

    doc = doc_ref.get()

    print(doc.to_dict())



