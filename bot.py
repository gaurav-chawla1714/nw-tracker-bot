import os

from dotenv import load_dotenv

from discord.ext import commands
from discord.ui import Button, View
import discord

from PIL import Image
import pytesseract
import re

from sheets_helpers import *
from time_helpers import *

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

custom_intents = discord.Intents.none()
custom_intents.message_content = True
custom_intents.guilds = True
custom_intents.guild_messages = True

bot = commands.Bot(command_prefix="!",
                   intents=custom_intents, help_command=None)

SUPPORTED_COMMANDS = ["status"]


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)

    await channel.send("NW Tracker is now online. Local time is " + get_formatted_local_datetime() + " (EST).")


@bot.command()
async def help(ctx, *args):
    if args:
        if args[0] == "status":
            await ctx.send('Type "!status t"')
        else:
            await ctx.send("Invalid command.")

    else:
        await ctx.send("Currently supported commands:\n1.) status")


@bot.command()
async def status(ctx, *args):
    if args:
        if args[0] == "t":
            await ctx.send("The local time is " + get_formatted_local_datetime() + " (EST).")
    else:
        await ctx.send("Please specify a type of status.")


class DatePickerView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Select Date Range", style=discord.ButtonStyle.primary, custom_id="select_date_range")
    async def select_date_range(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.add_month_buttons(interaction)
        await interaction.response.edit_message(content="Please select a month:", view=self)

    @discord.ui.button(label="Type Date Range", style=discord.ButtonStyle.primary, custom_id="type_date_range")
    async def type_date_range(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(content="Please enter the date range in the format `MM-DD-YYYY to MM-DD-YYYY`:", view=None)

    def add_month_buttons(self, interaction):
        for month in range(1, 13):
            month_button = Button(
                label=f"Month {month}", style=discord.ButtonStyle.secondary, custom_id=f"month_{month}")
            month_button.callback = self.month_button_callback
            self.add_item(month_button)

    async def month_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("we entered the month button callback")
        self.clear_items()
        self.add_day_buttons(self, interaction, int(button.label.split()[1]))
        await interaction.response.edit_message(content=f"Please select a day in {button.label}:", view=self)

    def add_day_buttons(self, interaction, month):
        for day in range(1, 31):
            day_button = Button(
                label=f"Day {day}", style=discord.ButtonStyle.secondary, custom_id=f"day_{day}")
            day_button.callback = self.day_button_callback  # Assigning the callback function
            self.add_item(day_button)

    async def day_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Placeholder: Handle day selection
        await interaction.response.send_message(f"You have selected {button.label}.", ephemeral=True)


@bot.command()
async def d(ctx):
    view = DatePickerView()
    await ctx.send("Click the button to enter a date range.", view=view)


@bot.command()
async def p(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please include an image to parse.")
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

        latest_row = read_sheet(service, "A2:A2")

        if not latest_row:
            await ctx.send("There is no value for the latest row number. Manually calculating which row the latest entry is in.")

            values = read_sheet(service, 'B4:E')

            latest_row_int = len(values) + 3

            if not update_sheet(service, 'A2:A2', [[str(latest_row_int)]]):
                await ctx.send("Something went wrong while updating the Google Sheet with the latest row number.")
                return

        else:
            latest_row_int = int(latest_row[0][0])

        latest_row_values = read_sheet(
            service, f'B{latest_row_int}:E{latest_row_int}')

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

            if not update_sheet(service, "A2:A2", [[str(current_row_num)]]):
                await ctx.send("Could not update the row counter!")
                return

        sheets_formatted_date = get_formatted_local_date()

        info_list = [[sheets_formatted_date, str(assets), str(
            abs(liabilities)), str(round(assets + liabilities, 2))]]

        range_name = f'B{current_row_num}:E{current_row_num}'

        if not update_sheet(service, range_name, info_list):
            await ctx.send("Something went wrong while updating the Google Sheet!")

        await ctx.send("Google Sheets successfully updated.")

        last_five_entries = read_sheet(
            service, f'B{current_row_num - 4}:E{current_row_num}')

        last_five_entries_str = "Here's the last 5 entries for net worth: \n"

        for entry in last_five_entries:
            date = entry[0]
            net_worth = entry[3]

            last_five_entries_str += f'{date}: {net_worth}\n'

        await ctx.send(last_five_entries_str)


### String formatting helper methods ###

def convert_money_to_float(money_str: str) -> float:
    return float(money_str.replace('$', '').replace(',', ''))


bot.run(BOT_TOKEN)
