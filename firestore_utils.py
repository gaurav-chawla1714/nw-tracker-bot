import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client as FirestoreClient

from custom_exceptions import FirestoreException

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH = os.getenv("FIRESTORE_SERVICE_ACCOUNT_PATH")

firestore_client: FirestoreClient = None

def create_firestore_client() -> FirestoreClient:
    global firestore_client

    if firestore_client is None:
        firebase_credentials = credentials.Certificate(FIRESTORE_SERVICE_ACCOUNT_PATH)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(firebase_credentials)

        firestore_client = firestore.client()

    return firestore_client

def firestore_test():
    db_client = create_firestore_client()

    doc_ref = db_client.collection('holdings-data').document('05092024')

    db_client = doc_ref.get()

    print(doc.to_dict())


def get_from_firestore(collection: str, document: str):
    db_client = create_firestore_client()

    try:
        return db_client.collection(collection).document(document).get().to_dict()
    except:
        raise FirestoreException

    # Add custom exception




