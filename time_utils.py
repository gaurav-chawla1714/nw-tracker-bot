### Time helper methods ###
from datetime import datetime, time
from typing import Final
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


DATA_START_DATE: Final[datetime] = datetime(2024, 2, 17)


def get_formatted_local_datetime() -> datetime:
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def get_formatted_local_date() -> str:
    now = datetime.now()

    return f'{now.month}/{now.day}/{now.year}'


def convert_to_datetime_object(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%m/%d/%Y")


def get_todays_date_firestore_doc_formatted() -> datetime:
    return datetime.combine(datetime.today(), time.min).strftime("%Y-%m-%d")


def get_firestore_doc_formatted_date(date: datetime) -> datetime:
    return date.strftime("%Y-%m-%d")


def get_todays_date_only() -> datetime:
    return datetime.combine(datetime.today(), time.min)


def datetimewithnanoseconds_to_datetime(dt_with_nanoseconds: DatetimeWithNanoseconds) -> datetime:
    return datetime(dt_with_nanoseconds.year, dt_with_nanoseconds.month, dt_with_nanoseconds.day)
