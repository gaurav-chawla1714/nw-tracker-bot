import os
from dotenv import load_dotenv

from firebase_admin import credentials, firestore
from google.cloud.firestore import Client as FirestoreClient

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH = os.getenv("FIRESTORE_SERVICE_ACCOUNT_PATH")

def create_firestore_client() -> FirestoreClient:
    firebase_credentials = credentials.Certificate(FIRESTORE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(firebase_credentials)

    return firestore.client()

def firestore_test():
    db_client = create_firestore_client()

    doc_ref = db_client.collection('holdings-data').document('05092024')

    db_client = doc_ref.get()

    print(doc.to_dict())


def get_from_firestore(collection: str, document: str, db_client: FirestoreClient = None):

    if not client:
        db_client = create_firestore_client()

    return db_client.collection(collection).document(document).get()




