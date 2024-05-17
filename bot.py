import os
import calendar
import math
import asyncio

from dotenv import load_dotenv

from discord.ext import commands
from discord.ui import Button, View
import discord

from PIL import Image
import pytesseract
import re

from table2ascii import table2ascii as t2a, PresetStyle

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from dateutil import parser as date_parser

from sheets_utils import *
from time_utils import *
from firestore_utils import *

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')
USER_ID = os.getenv('USER_ID')

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


class DateOptionsView(View):
    def __init__(self, future: asyncio.Future[str]):
        super().__init__()
        self.future: asyncio.Future[str] = future

    @discord.ui.button(label="Select Date Range", style=discord.ButtonStyle.primary, custom_id="select_date_range")
    async def select_date_range(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.stop()

        if not self.future.done():
            self.future.set_result("Select Date Range")

    @discord.ui.button(label="Type Date Range", style=discord.ButtonStyle.primary, custom_id="type_date_range")
    async def type_date_range(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.stop()

        if not self.future.done():
            self.future.set_result("Type Date Range")


class DatePickerView(View):
    def __init__(self, message, future: asyncio.Future[str], is_starting: bool, is_ending: bool, user_selected_start_date: datetime = None):
        super().__init__()
        self.message = message

        self.selected_year: str = ""
        self.selected_month: str = ""
        self.selected_day: str = ""

        self.starting_date: datetime = DATA_START_DATE
        self.ending_date: datetime = datetime.today()

        self.is_starting: bool = is_starting
        self.is_ending: bool = is_ending

        self.future: asyncio.Future[str] = future

        self.add_year_buttons()

    def add_year_buttons(self):
        for year in range(2024, self.ending_date.year + 1):
            year = str(year)
            year_button = Button(
                label=year, style=discord.ButtonStyle.secondary, custom_id=f"year_{year}")
            year_button.callback = lambda interaction, year=year: self.year_button_callback(
                interaction, year)
            self.add_item(year_button)

    async def year_button_callback(self, interaction: discord.Interaction, year: str):
        self.selected_year = year
        self.clear_items()
        self.add_month_buttons()
        await self.message.edit_message(content=f"Please select a month in {year}:", view=self)

    def add_month_buttons(self):
        i = 0
        eligible_months = calendar.month_name[1:]

        if self.is_starting:
            if int(self.selected_year) == self.starting_date.year:  # restriction on beginning months
                eligible_months = eligible_months[1:]  # February onwards

            if int(self.selected_year) == self.ending_date.year:  # restriction on ending months
                end_index = eligible_months.index(
                    calendar.month_name[self.ending_date.month])

                eligible_months = eligible_months[0:end_index + 1]

        for month in eligible_months:
            month_button = Button(
                label=month, row=math.floor(i/3), style=discord.ButtonStyle.secondary, custom_id=f"month_{month}")
            month_button.callback = lambda interaction, month=month: self.month_button_callback(
                interaction, month)
            self.add_item(month_button)
            i += 1

    async def month_button_callback(self, interaction: discord.Interaction, month: str):
        self.selected_month = month
        self.clear_items()
        self.add_day_buttons()
        await interaction.response.edit_message(content=f"Please select a day in {month} {self.selected_year}:", view=self)

    def add_day_buttons(self):

        start_day = 1
        month = self.selected_month  # str representation

        month_num = calendar.month_name[:].index(month)

        if int(self.selected_year) == DATA_START_DATE.year and month_num == DATA_START_DATE.month:
            start_day = DATA_START_DATE.day

        _, num_days_in_month = calendar.monthrange(
            int(self.selected_year), month_num)

        print(num_days_in_month)

        print(month_num)

        # convert month into its int
        # calendar module -> how many days in month
        # beginning restriction if feb 2024
        # end restriction if same as end month/year
        for day in range(start_day, 26):
            day_button = Button(
                label=day, style=discord.ButtonStyle.secondary, custom_id=f"day_{day}")
            day_button.callback = lambda interaction, day=day: self.day_button_callback(
                interaction, day)
            self.add_item(day_button)

    async def day_button_callback(self, interaction: discord.Interaction, day: str):
        self.stop()

        self.selected_day = day

        if not self.future.done():
            self.future.set_result(
                f'{self.selected_month} {self.selected_day}, {self.selected_year}')

    def disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True  # Disable the button

    async def add_reactions(self):
        await self.message.add_reaction("◀️")


@bot.command()
async def d(ctx):
    date_option_future = asyncio.Future()

    date_option_view = DateOptionsView(date_option_future)
    date_choice_message = await ctx.send("Please choose whether you prefer to select or type the date.", view=date_option_view)

    try:
        date_choice = await asyncio.wait_for(date_option_future, timeout=120.0)
        await date_choice_message.delete()
    except asyncio.TimeoutError:
        await ctx.send("You didn't complete the date option selection within 120 seconds.")
        return

    if date_choice == 'Select Date Range':

        start_date_future = asyncio.Future()

        starting_date_message = await ctx.send("Starting date: ")
        ending_date_message = await ctx.send("Ending date: ")

        start_date_message = await ctx.send("Select a year for the starting date: ")
        start_date_picker_view = DatePickerView(message=start_date_message,
                                                future=start_date_future, is_starting=True, is_ending=False)

        try:
            selected_date = await asyncio.wait_for(start_date_future, timeout=120.0)
            await starting_date_message.edit(content=f'Starting date: {selected_date}')

        except asyncio.TimeoutError:
            await ctx.send("You didn't complete the date selection within 120 seconds.")
            start_date_picker_view.disable_all_buttons()
            return

        await start_date_message.delete()

        # End Date

        end_date_future = asyncio.Future()

        end_date_picker_view = DatePickerView(
            future=end_date_future, is_starting=False, is_ending=True)

        end_date_message = await ctx.send("Select a year for the ending date: ", view=end_date_picker_view)

        try:
            selected_date = await asyncio.wait_for(end_date_future, timeout=120.0)
            await ending_date_message.edit(content=f'Ending date: {selected_date}')

        except asyncio.TimeoutError:
            await ctx.send("You didn't complete the date selection within 120 seconds.")
            end_date_picker_view.disable_all_buttons()
            return

        await end_date_message.delete()

    elif date_choice == 'Type Date Range':
        await ctx.send("You selected Type Date Range")
    else:
        await ctx.send("something went wrong...")


@bot.command()
async def p(ctx):
    if not ctx.message.attachments:
        await ctx.send("Please include an image to parse.")
    else:
        attachment = ctx.message.attachments[0]

        await attachment.save("temp_image.png")

        text = pytesseract.image_to_string(Image.open("temp_image.png"))

        os.remove("temp_image.png")

        pattern = r'\$\d{1,3}(?:,\d{3})*\.\d{2}\s*[-]\s*\$\d{1,3}(?:,\d{3})*\.\d{2}'
        matches = re.findall(pattern, text)

        nw_list = matches[0].split(" ")

        assets = money_to_float(nw_list[0])
        # liabilities should be positive, for consistency (unlike screenshot)
        liabilities = abs(money_to_float(nw_list[1]))

        await ctx.send(f'Assets: {"${:,.2f}".format(assets)}\nLiabilities: {"${:,.2f}".format(liabilities)}\nNet Worth: {"${:,.2f}".format(round(assets - liabilities, 2))}')

        try:
            latest_row_int = get_latest_row_int()
        except GoogleSheetException:
            await ctx.send("Something went wrong while updating the Google Sheet with the latest row number.")
            return

        latest_row_values = read_sheet(
            f'{NW_START_COLUMN}{latest_row_int}:{NW_END_COLUMN}{latest_row_int}')

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

            if not update_sheet("A2:A2", [[str(current_row_num)]]):
                await ctx.send("Could not update the row counter!")
                return

        info_list = [[get_formatted_local_date(), str(assets), str(
            liabilities), str(round(assets - liabilities, 2))]]

        if not update_sheet(f'{NW_START_COLUMN}{current_row_num}:{NW_END_COLUMN}{current_row_num}', info_list):
            await ctx.send("Something went wrong while updating the Google Sheet!")
            return

        nw_data = NetWorthDataFirestore(
            assets, liabilities, round(assets - liabilities, 2))

        put_in_firestore(
            'daily-snapshots', get_todays_date_firestore_doc_formatted(), nw_data.to_dict())

        await ctx.send("Google Sheets/Firestore successfully updated. Here's the last 5 entries for net worth:")

        await prev(ctx, "5")  # displays last 5 entries


@bot.command()
async def prev(ctx, *args):
    num_entries = get_num_nw_entries()
    prev_entries = 5  # default, if no args are passed in

    if args:
        try:
            if args[0] == "all":
                prev_entries = num_entries
            elif int(args[0]) <= num_entries:
                prev_entries = int(args[0])

        except ValueError:
            await ctx.send("Argument is not a valid integer. Defaulting to the previous 5 entries.")

    latest_row_int = get_latest_row_int()

    entries = read_sheet(
        f'{NW_START_COLUMN}{latest_row_int - prev_entries + 1}:{NW_END_COLUMN}{latest_row_int}')

    selected_output = [[entry[0], entry[3]] for entry in entries]

    table = t2a(
        header=["Date", "Net Worth"],
        body=selected_output,
        first_col_heading=True,
        style=PresetStyle.thin_compact
    )

    await ctx.send(f'```\n{table}\n```')


@bot.command()
async def holdings(ctx, *args):  # NOT FINISHED
    ALL_HOLDINGS = ["VT", "VTI", "VXUS", "VINIX",
                    "VMCIX", "VSCIX", "VTSNX", "VUSXX", "SPAXX"]
    args_list = []
    if args:
        await ctx.send(args)
        if args[0] == "all":
            args_list = ALL_HOLDINGS
        else:
            for arg in args:
                if arg in ALL_HOLDINGS:
                    if arg not in args_list:  # duplicates protection
                        args_list.append(arg)
                else:
                    await ctx.send("Invalid argument detected. Defaulting to showing all holdings.")
                    args_list = ALL_HOLDINGS
                    break
    else:
        await ctx.send("No arguments detected. Defaulting to showing all holdings.")
        args_list = ALL_HOLDINGS

    await ctx.send(args_list)


@bot.command()
async def t(ctx):
    nw_data = NetWorthDataFirestore(
        assets=3.39, liabilities=3.11, net_worth=0.28)

    put_in_firestore('daily-snapshots',
                     get_todays_date_firestore_doc_formatted(), nw_data.to_dict())


@bot.command()
async def graph(ctx, start_date_str: str = None, end_date_str: str = None):

    start_date = None
    end_date = None

    # Parse start date
    if start_date_str:
        try:
            start_date = date_parser.parse(start_date_str)

            if start_date < DATA_START_DATE:
                await ctx.send("Start date must be after 02/17/2024. Defaulting to no date restrictions for the graph.")
                start_date = None
        except ValueError:
            await ctx.send("Invalid start date format. Please use MM/DD/YYYY.")

    # Parse end date
    # if start_date is None, then previous code block didn't succeed in parsing the date.
    if start_date and end_date_str:
        try:
            end_date = date_parser.parse(end_date_str)

            if start_date < DATA_START_DATE:
                await ctx.send("End date must be after 02/17/2024. Defaulting to no end restriction.")
                start_date = None
        except ValueError:
            await ctx.send("Invalid end date format. Please use MM/DD/YYYY. Defaulting to no end restriction.")

    if start_date and end_date and end_date < start_date:
        await ctx.send("End date must be later than start date. Defaulting to no date restrictions for the graph")
        start_date = None
        end_date = None

    if not start_date:
        start_date = DATA_START_DATE
    if not end_date:
        # initialize current datetime to midnight for consistency when comparing
        end_date = datetime.combine(datetime.today(), time.min)

    latest_row_int = get_latest_row_int()

    values = read_sheet(
        f'{NW_START_COLUMN}{NW_START_ROW}:{NW_END_COLUMN}{latest_row_int}')

    dates = [datetime.strptime(entry[0], '%m/%d/%Y') for entry in values if start_date <=
             datetime.strptime(entry[0], '%m/%d/%Y') <= end_date]

    nw_values = [money_to_float(entry[3]) for entry in values if start_date <= datetime.strptime(
        entry[0], '%m/%d/%Y') <= end_date]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, nw_values, linestyle='-', color='b')

    plt.xlabel('Date')
    plt.ylabel('NW')

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    max_nw = max(nw_values)
    min_nw = min(nw_values)
    graph_pad = max_nw * 0.15
    ax.set_ylim(min_nw - graph_pad, max_nw + graph_pad)

    plt.gcf().autofmt_xdate()

    plt.savefig('temp_graph.png')
    plt.close()

    with open('temp_graph.png', 'rb') as file:
        await ctx.send(file=discord.File(file, 'plot.png'))

    os.remove("temp_graph.png")


@bot.command()
async def transfer(ctx):  # temporary script to transfer data from sheets to firestore
    #     values = read_sheet(f'{NW_START_COLUMN}{NW_START_ROW}:{NW_END_COLUMN}')

    #     for row in values:
    #         date: datetime = date_parser.parse(row[0])

    #         assets: float = money_to_float(row[1])
    #         liabilities: float = money_to_float(row[2])
    #         net_worth: float = money_to_float(row[3])

    #         # print(
    #         #     f'Date: {date}, Assets: {assets}, Liabilities: {liabilities}, NW: {net_worth}')

    #         nw_data = NetWorthDataFirestore(assets, liabilities, net_worth, date)

    #         put_in_firestore(
    #             'daily-snapshots', get_firestore_doc_formatted_date(date), nw_data.to_dict())
    return


@bot.command()
async def verify(ctx):

    if ctx.author.id != USER_ID:
        return

    sheets_values = read_sheet(
        f'{NW_START_COLUMN}{NW_START_ROW}:{NW_END_COLUMN}')

    # dates_list: List[datetime] = [
    #     get_firestore_doc_formatted_date(date_parser.parse(row[0])) for row in sheets_values]

    # print(dates_list)

    for row in sheets_values:
        date: datetime = date_parser.parse(row[0])

        assets: float = money_to_float(row[1])
        liabilities: float = money_to_float(row[2])
        net_worth: float = money_to_float(row[3])

        doc = get_from_firestore(
            'daily-snapshots', get_firestore_doc_formatted_date(date))

        if date == datetimewithnanoseconds_to_datetime(doc["date"]) and assets == doc["assets"] and liabilities == doc["liabilities"] and net_worth == doc["net_worth"]:
            continue
        else:
            await ctx.send(f'{row[0]} is NOT the same! Please verify manually. Exiting now...')
            return

    await ctx.send("Everything is verified to be the same!")


## String formatting helper methods ###


def money_to_float(money_str: str) -> float:
    return float(money_str.replace('$', '').replace(',', ''))


bot.run(BOT_TOKEN)
