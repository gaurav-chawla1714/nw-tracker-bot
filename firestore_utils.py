import os
from dotenv import load_dotenv
from typing import Final, Dict, Any
from datetime import datetime, time

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

from custom_exceptions import FirestoreException

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH: Final[str] = os.getenv(
    "FIRESTORE_SERVICE_ACCOUNT_PATH")

firestore_client: Client = None


class NetWorthData:
    def __init__(self, assets: float, liabilities: float, net_worth: float):
        self.assets = assets
        self.liabilities = liabilities
        self.net_worth = net_worth

        self.date: datetime = datetime.combine(datetime.today(), time.min)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assets": self.assets,
            "liabilities": self.liabilities,
            "net_worth": self.net_worth,
            "date": self.date
        }


def create_firestore_client() -> Client:
    global firestore_client

    if firestore_client is None:
        firebase_credentials = credentials.Certificate(
            FIRESTORE_SERVICE_ACCOUNT_PATH)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(firebase_credentials)

        firestore_client = firestore.client()

    return firestore_client


def get_from_firestore(collection: str, document: str) -> Dict[str, Any]:
    db_client = create_firestore_client()

    try:
        return db_client.collection(collection).document(document).get().to_dict()
    except:
        raise FirestoreException

    # Add custom exception


def put_in_firestore(collection: str, document: str, data: Dict[str, Any]):

    db_client = create_firestore_client()

    doc_ref = db_client.collection(collection).document(document)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update(data)
    else:
        doc_ref.set(data)
