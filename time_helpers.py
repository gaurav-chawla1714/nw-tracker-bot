### Time helper methods ###
from datetime import datetime


def get_formatted_local_datetime():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def get_formatted_local_date():
    now = datetime.now()

    return f'{now.month}/{now.day}/{now.year}'


def convert_to_datetime_object(date_str: str):
    return datetime.strptime(date_str, "%m/%d/%Y")
