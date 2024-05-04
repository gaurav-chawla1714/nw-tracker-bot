### Google Sheets API helper methods ###
import os
from dotenv import load_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

API_SCOPES = os.getenv("API_SCOPES").split()
SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')


def create_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=API_SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    return service


def read_sheet(service, range_name) -> list:
    sheet = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()

    return sheet.get('values', [])


def update_sheet(service, range_name: str, data: list) -> bool:
    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                               range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False
