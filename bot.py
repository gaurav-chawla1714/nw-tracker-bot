import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from PIL import Image
import re
import pytesseract
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

API_SCOPES = os.getenv("API_SCOPES").split()
SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

custom_intents = discord.Intents.none()
custom_intents.message_content = True
custom_intents.guilds = True
custom_intents.guild_messages = True

bot = commands.Bot(command_prefix="!",
                   intents=custom_intents, help_command=None)


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)

    await channel.send("NW Tracker is now online. Local time is " + get_formatted_local_datetime() + " (EST).")


@bot.command()
async def help(ctx, *args):
    if args:
        if args[0] == "status":
            await ctx.send('Write !status + "t"')
        else:
            await ctx.send("Invalid command.")

    else:
        await ctx.send("supported help commands: status")


@bot.command()
async def status(ctx, *args):
    if args:
        if args[0] == "t":
            await ctx.send("The local time is " + get_formatted_local_datetime() + " (EST).")
    else:
        await ctx.send("You didn't specify what status you wanted.")


@bot.command()
async def a(ctx):
    sheets_service = create_sheets_service()

    latest_row = read_sheet(service=sheets_service, range_name="B1:B1")

    if not latest_row:
        await ctx.send("There is no value for the latest row. Manually calculating the latest row...")
        return
        # manual calculation
    else:
        latest_row_int = int(latest_row[0][0])

    latest_row_values = read_sheet(
        service=sheets_service, range_name=f'B{latest_row_int}:E{latest_row_int}')

    if not latest_row_values:
        await ctx.send("There doesn't seem to be an entry for today's date. Creating new entry...")
    else:
        latest_row_date = latest_row_values[0][0]
        todays_date = get_formatted_local_date()

        latest_row_date_object = convert_to_datetime_object(latest_row_date)
        todays_date_object = convert_to_datetime_object(todays_date)

        if todays_date_object < latest_row_date_object:
            await ctx.send("Somehow, today's date is before the latest entry date. The Sheet needs to be manually inspected.")
            return

        elif todays_date_object == latest_row_date_object:
            await ctx.send("There is already an entry for today. The row will be overwritten with the updates values.")

        else:
            await ctx.send("There is no existing entry for today. A new row will be created.")

            time.sleep(3)


@bot.command()
async def p(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please include an image for me to parse.")
    else:
        attachment = ctx.message.attachments[0]

        await attachment.save("temp_image.png")

        text = pytesseract.image_to_string(Image.open("temp_image.png"))

        pattern = r'\$\d{1,3}(?:,\d{3})*\.\d{2}\s*[-]\s*\$\d{1,3}(?:,\d{3})*\.\d{2}'
        matches = re.findall(pattern, text)

        nw_list = matches[0].split(" ")

        assets = convert_money_to_float(nw_list[0])
        liabilities = convert_money_to_float(nw_list[1])

        await ctx.send(f'Assets: ${str(assets)}\nLiabilities: ${str(liabilities)}\nNet Worth: ${str(round(assets + liabilities, 2))}')

        sheets_service = create_sheets_service()

        latest_row = int(read_sheet(
            service=sheets_service, range_name="B1:B1")[0][0])

        latest_row_date = read_sheet(
            service=sheets_service, range_name=f'B{latest_row}:E{latest_row}')

        print(latest_row_date)

        # current_row = latest_row + 1

        # if not update_sheet(service=sheets_service, range_name="B1:B1", data=[[str(current_row)]]):
        #     await ctx.send("Could not update the row counter!")
        #     return

        # sheets_formatted_time = get_formatted_local_datetime()

        # info_list = [[sheets_formatted_time, str(assets), str(abs(liabilities)), str(round(assets + liabilities, 2))]]
        # range_name = f'B{current_row}:E{current_row}'

        # if update_sheet(service=sheets_service, range_name=range_name, data=info_list):
        #     await ctx.send("Google Sheets successfully updated.")
        # else:
        #     await ctx.send("Something went wrong while updating the Google Sheet!")

        # fetch latest row
        # check to see if date is the same as today's date
        # if it is, overwrite existing entry
        # if not, create entry on next line for the new date


### Time helper methods ###

def get_formatted_local_datetime():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def get_formatted_local_date():
    return datetime.now().strftime("%m/%d/%Y")


def convert_to_datetime_object(date_str: str):
    return datetime.strptime(date_str, "%m/%d/%Y")


### String formatting helper methods ###

def convert_money_to_float(money_str: str) -> float:
    return float(money_str.replace('$', '').replace(',', ''))


### Google Sheets API helper methods ###

def create_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=API_SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    return service


def read_sheet(service, range_name) -> list:
    sheet = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = sheet.get('values', [])
    if not values:
        print('No data found.')
    return values


def update_sheet(service, range_name: str, data: list) -> bool:
    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                               range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False


bot.run(BOT_TOKEN)
