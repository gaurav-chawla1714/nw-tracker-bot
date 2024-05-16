### Time helper methods ###
from datetime import datetime, time
from typing import Final


DATA_START_DATE: Final[datetime] = datetime(2024, 2, 17)


def get_formatted_local_datetime() -> datetime:
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def get_formatted_local_date() -> str:
    now = datetime.now()

    return f'{now.month}/{now.day}/{now.year}'


def convert_to_datetime_object(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%m/%d/%Y")
