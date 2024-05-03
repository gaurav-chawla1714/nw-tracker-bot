import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from PIL import Image
import re
import pytesseract
import time
import datetime
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

bot = commands.Bot(command_prefix="!", intents=custom_intents, help_command=None)


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)

    await channel.send("NW Tracker is now online. Local time is " + get_local_time())

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
            await ctx.send("The local time is " + get_local_time())
    else:
        await ctx.send("You didn't specify what status you wanted.")

@bot.command()
async def r(ctx):
    sheets_service = create_sheets_service()

    values = read_sheet(sheets_service, "A1:AA100")

    await ctx.send(values)


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

        latest_row = int(read_sheet(service=sheets_service, range_name="B1:B1")[0][0])

        current_row = latest_row + 1

        if not update_sheet(service=sheets_service, range_name="B1:B1", data=[[str(current_row)]]):
            await ctx.send("Could not update the row counter!")
            return

        sheets_formatted_time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        info_list = [[sheets_formatted_time, str(assets), str(abs(liabilities)), str(round(assets + liabilities, 2))]]
        range_name = f'B{current_row}:E{current_row}'

        if update_sheet(service=sheets_service, range_name=range_name, data=info_list):
            await ctx.send("Google Sheets successfully updated.")
        else:
            await ctx.send("Something went wrong while updating the Google Sheet!")







def get_local_time():
    return datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " (EST)."

def convert_money_to_float(money_str: str) -> float:
    return float(money_str.replace('$', '').replace(',', ''))

def create_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=API_SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    return service

def read_sheet(service, range_name) -> list:
    sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = sheet.get('values', [])
    if not values:
        print('No data found.')
    return values

def update_sheet(service, range_name: str, data: list) -> bool:
    body = {'values': data}
    try:
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption="USER_ENTERED", body=body).execute()
        return True
    except:
        return False



bot.run(BOT_TOKEN)