
import os
from datetime import datetime

from dotenv import load_dotenv

from discord.ext import commands
import discord

from PIL import Image
import pytesseract
import re

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

        service = create_sheets_service()

        latest_row = read_sheet(service=service, range_name="A2:A2")

        if not latest_row:
            await ctx.send("There is no value for the latest row. Manually calculating the latest row...")
            return
            # manual calculation
            # latest_row_int =
        else:
            latest_row_int = int(latest_row[0][0])

        latest_row_values = read_sheet(
            service=service, range_name=f'B{latest_row_int}:E{latest_row_int}')

        try:
            latest_row_date = latest_row_values[0][0]
        except IndexError:
            await ctx.send("Discrepancy between latest row index and Sheet file. Fix is in progress.")
            return
        todays_date = get_formatted_local_date()

        latest_row_date_object = convert_to_datetime_object(latest_row_date)
        todays_date_object = convert_to_datetime_object(todays_date)

        if todays_date_object < latest_row_date_object:
            await ctx.send("Somehow, today's date is before the latest entry date. The Sheet needs to be manually inspected.")
            return

        elif todays_date_object == latest_row_date_object:
            await ctx.send("There's already an entry for today. The row will be overwritten with the updated values.")

            current_row_num = latest_row_int

        else:
            await ctx.send("There's no existing entry for today. A new row will be created.")

            current_row_num = latest_row_int + 1

            if not update_sheet(service=service, range_name="A2:A2", data=[[str(current_row_num)]]):
                await ctx.send("Could not update the row counter!")
                return

        sheets_formatted_date = get_formatted_local_date()

        info_list = [[sheets_formatted_date, str(assets), str(
            abs(liabilities)), str(round(assets + liabilities, 2))]]

        range_name = f'B{current_row_num}:E{current_row_num}'

        if update_sheet(service=service, range_name=range_name, data=info_list):
            await ctx.send("Google Sheets successfully updated.")
        else:
            await ctx.send("Something went wrong while updating the Google Sheet!")


### Time helper methods ###

def get_formatted_local_datetime():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def get_formatted_local_date():
    now = datetime.now()

    return f'{now.month}/{now.day}/{now.year}'


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

    return sheet.get('values', [])


def update_sheet(service, range_name: str, data: list) -> bool:
    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                               range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False


bot.run(BOT_TOKEN)
