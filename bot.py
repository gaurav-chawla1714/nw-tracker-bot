import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from PIL import Image
import re
import pytesseract
import time
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
        message_timestamp = ctx.message.created_at

        await attachment.save("temp_image.png")

        await ctx.send(message_timestamp)

        text = pytesseract.image_to_string(Image.open("temp_image.png"))

        pattern = r'\$\d{1,3}(?:,\d{3})*\.\d{2}\s*[-]\s*\$\d{1,3}(?:,\d{3})*\.\d{2}'
        matches = re.findall(pattern, text)

        nw_list = matches[0].split(" ")

        assets = convert_money_to_float(nw_list[0])
        liabilities = convert_money_to_float(nw_list[1])

        await ctx.send(f'Assets: ${str(assets)}')
        await ctx.send(f'Liabilities: ${str(liabilities)}')
        await ctx.send(f'Net Worth: ${str(round(assets + liabilities, 2))}')





def get_local_time():
    return time.strftime("%H:%M:%S", time.localtime()) + " (EST)."

def convert_money_to_float(money_str: str) -> float:
    return float(money_str.replace('$', '').replace(',', ''))

def create_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=API_SCOPES)

    service = build('sheets', 'v4', credentials=credentials)

    return service

def read_sheet(service, range_name):
    sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    values = sheet.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)

    return values


bot.run(BOT_TOKEN)