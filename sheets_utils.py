### Google Sheets API helper methods ###
import os
from typing import List, Final
from dotenv import load_dotenv

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource

from time_utils import *
from custom_exceptions import GoogleSheetException

load_dotenv()

SHEETS_API_SCOPES: Final[List[str]] = os.getenv("SHEETS_API_SCOPES").split()
SHEETS_SERVICE_ACCOUNT_PATH: Final[str] = os.getenv(
    "SHEETS_SERVICE_ACCOUNT_PATH")
SPREADSHEET_ID: Final[str] = os.getenv('SPREADSHEET_ID')

NW_START_COLUMN: Final[str] = 'B'
NW_START_ROW: Final[str] = '4'
NW_END_COLUMN: Final[str] = 'E'

LATEST_ROW_CELL: Final[str] = 'A2'

# add holdings constants


sheets_service: Resource = None


def create_sheets_service() -> Resource:
    global sheets_service

    if sheets_service is None:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                SHEETS_SERVICE_ACCOUNT_PATH, scopes=SHEETS_API_SCOPES)

            sheets_service = build('sheets', 'v4', credentials=credentials)
        except:
            raise GoogleSheetException(
                "Something went wrong when creating the Sheets Service!")

    return sheets_service


def read_sheet(range_name: str) -> List[List[str]]:

    service = create_sheets_service()

    sheet = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()

    return sheet.get('values', [])


def update_sheet(range_name: str, data: List[List[str]]) -> bool:

    service = create_sheets_service()

    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                               range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False


def get_latest_row_int() -> int:

    latest_row = read_sheet(f'{LATEST_ROW_CELL}:{LATEST_ROW_CELL}')

    if not latest_row:

        latest_row_int = get_num_nw_entries() + 3

        if not update_sheet(f'{LATEST_ROW_CELL}:{LATEST_ROW_CELL}', [[str(latest_row_int)]]):
            raise GoogleSheetException

    else:
        latest_row_int = int(latest_row[0][0])

    return latest_row_int


def get_next_nw_entry_row() -> int:
    """
    For the net worth section of the sheets document, determines the next row to place data.
    If the data in the latest row is from the same date as the current date, indicate to overwrite existing latest row. 
    Else, if it is from a previous date, indicate to create a new row.

    Returns:
        int: The row in which to place the next row of data
    """

    try:
        latest_row_int = get_latest_row_int()
    except GoogleSheetException:
        raise GoogleSheetException(
            "Error when trying to access the latest row int!")

    latest_row_values = read_sheet(
        f'{NW_START_COLUMN}{latest_row_int}:{NW_END_COLUMN}{latest_row_int}')

    try:
        latest_row_date_object = convert_to_datetime_object(
            latest_row_values[0][0])
    except IndexError:
        raise GoogleSheetException(
            "There was not a value in the date column of the latest row!")

    todays_date_object = get_todays_date_only()

    if todays_date_object < latest_row_date_object:
        raise GoogleSheetException(
            "todays date is less than date in latest entry somehow")

    elif todays_date_object == latest_row_date_object:
        current_row_int = latest_row_int
    else:
        current_row_int = latest_row_int + 1

    if not update_sheet(f'{LATEST_ROW_CELL}:{LATEST_ROW_CELL}', [[str(current_row_int)]]):
        raise GoogleSheetException("Could not update the row counter!")

    return current_row_int
