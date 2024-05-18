import os
from dotenv import load_dotenv
from typing import Final, Dict, Any, List

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import aggregation, Client, Query
from google.cloud.firestore_v1.base_query import FieldFilter

from custom_exceptions import FirestoreException

load_dotenv()

FIRESTORE_SERVICE_ACCOUNT_PATH: Final[str] = os.getenv(
    "FIRESTORE_SERVICE_ACCOUNT_PATH")

firestore_client: Client = None


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


def get_previous_nw_entries(limit: int = None) -> List[Dict[str, Any] | None]:

    db_client = create_firestore_client()

    # tests for existence of
    query = (
        db_client.collection('nw-data')
        .order_by('date', direction=firestore.Query.DESCENDING)
    )

    if limit:
        query.limit(limit)

    results = query.stream()
    documents = [doc.to_dict() for doc in results]
    return documents


def execute_query(query: Query) -> List[Dict[str, Any] | None]:
    results = query.stream()
    documents = [doc.to_dict() for doc in results]
    return documents


def get_num_nw_entries() -> int:
    """
    Returns the total number of documents in the nw-data collection

    Returns:
        int: The total number of documents in the nw-data collection.
    """

    db_client = create_firestore_client()

    query = (
        db_client.collection('nw-data')
        .where(filter=FieldFilter("net_worth", ">=", 0))
    )

    aggregate_query = aggregation.AggregationQuery(query)

    results = aggregate_query.count(alias="all").get()

    return results[0][0].value
