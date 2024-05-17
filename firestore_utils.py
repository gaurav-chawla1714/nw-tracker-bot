import os
from dotenv import load_dotenv
from typing import Final, Dict, Any
from datetime import datetime, time

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

from custom_exceptions import FirestoreException

from time_utils import *

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH: Final[str] = os.getenv(
    "FIRESTORE_SERVICE_ACCOUNT_PATH")

firestore_client: Client = None


class NetWorthDataFirestore:
    def __init__(self, assets: float, liabilities: float, net_worth: float, date: datetime = None):
        self.assets: float = assets
        self.liabilities: float = liabilities
        self.net_worth: float = net_worth

        if not date:
            self.date: datetime = get_todays_date_only()
        else:
            self.date: datetime = date

    def to_dict(self) -> Dict[str, float | datetime]:
        return {
            "assets": self.assets,
            "liabilities": self.liabilities,
            "net_worth": self.net_worth,
            "date": self.date
        }


class HoldingsDataFirestore:
    def __init__(self, holdings: Dict[str, float], date: datetime = None):
        self.holdings = holdings

        if not date:
            self.date: datetime = get_todays_date_only()
        else:
            self.date: datetime = date

    def to_dict(self) -> Dict[str, Dict[str, float] | datetime]:
        return {
            "holdings": self.holdings,
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
