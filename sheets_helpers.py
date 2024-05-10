### Google Sheets API helper methods ###
import os
from typing import List
from dotenv import load_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

from custom_exceptions import GoogleSheetException

load_dotenv()

SHEETS_API_SCOPES = os.getenv("SHEETS_API_SCOPES").split()
SHEETS_SERVICE_ACCOUNT_PATH = os.getenv("SHEETS_SERVICE_ACCOUNT_PATH")
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')


def create_sheets_service() -> Resource:
    credentials = service_account.Credentials.from_service_account_file(
        SHEETS_SERVICE_ACCOUNT_PATH, scopes=SHEETS_API_SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    return service


def read_sheet(range_name: str, service: Resource = None) -> List[List[str]]:
    sheet = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()

    return sheet.get('values', [])


def update_sheet(range_name: str, data: List[List[str]], service: Resource = None) -> bool:

    if not service:
        service = create_sheets_service()

    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                               range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False


def get_latest_row_int(service: Resource = None) -> int:

    if not service:
        service = create_sheets_service()

    latest_row = read_sheet("A2:A2", service)

    if not latest_row:
        values = read_sheet('B4:E', service)

        latest_row_int = len(values) + 3

        if not update_sheet('A2:A2', [[str(latest_row_int)]], service):
            raise GoogleSheetException

    else:
        latest_row_int = int(latest_row[0][0])

    return latest_row_int


def get_number_of_entries(service: Resource = None) -> int:
    """
    Returns the total number of data entries in the Sheet (1 row/date = 1 entry). Creates own Sheets Resource if not passed in.

    Args:
        service (Resource): Google Resource to interact with the Google Sheets API.

    Returns:
        int: The total number of data entries in the Sheet.
    """

    if not service:
        service = create_sheets_service()

    values = read_sheet('B4:E', service)

    return len(values)
