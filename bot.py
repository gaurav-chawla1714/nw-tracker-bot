import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
from PIL import Image
import re
import pytesseract
import time

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

BOT_TOKEN = os.getenv('BOT_TOKEN')

CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None,)

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
async def p(ctx):
    if ctx.message.attachments:
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

bot.run(BOT_TOKEN)