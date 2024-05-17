# How to run: (not finished)

- `pip install -r requirements.txt`
- In an .env file, define the following:
  - `BOT_TOKEN` Your Discord bot token, found on the developer portal
  - `CHANNEL_ID` The channel ID of the channel you want the bot to message in
  - `TESSERACT_PATH` The filepath where you have Tesseract OCR installed
  - `SHEETS_API_SCOPES` The Google Sheets API Scopes that define the level of access granted to your Google Sheets applications (learn more at https://developers.google.com/sheets/api/scopes)
  - `SHEETS_SERVICE_ACCOUNT_PATH`
- `python bot.py`

# Features

## In-Progress Features:

- Integrate Google Firestore NoSQL Database as primary database

  - ~~Establish "schema"~~ ✅
  - All current and future data should also be stored in Firestore from now on. 🚧
  - All existing data needs to be migrated over.

- Deprecate Google Sheets as primary read source

  - All methods where data is read in from Google Sheets should be converted to Firestore queries.

- NW graphing functionality. Ability for custom date bounds

  - ~~Integrate as basic "!" command~~ ✅
  - Refactor into a slash command for better argument hints

## Upcoming Features:

- Yahoo Finance API Integration
  - real-time pricing data for real-time estimated nw calculations.
  - can only happen after parsing Fidelity account view xslx
- Updated help command to list out all of the existing commands
  - Right now, the only one is status
- Parse Fidelity account view xslx to update holdings. Use pandas to parse excel file.
- Custom indexes on Firestore database for date field, to allow for quick range calculation.
- Integrate custom exceptions more, including messages. Integrate on read commands as well.
- Finish readme tutorial writeup

## Backlog:

- Date picking functionality
  - start date day restrictions need to be implemented
  - end date year, month, day restrictions need to be implemented
  - once dates are collected, need to do actual queries

## Wish List:

- Cloud hosting? Raspberry Pi hosting?
- Convert everything into slash commands?

# Bug Fixes

## In-Progress Fixes:

- N/A

## Upcoming fixes:

- Updating docstrings for existing methods

## Backlog:

- Date picking functionality bugs
  - asyncio.TimeoutError does not properly disable buttons

# Recently Finished Features

- Generalize sheets queries with NW_START_COLUMN, NW_START_ROW, NW_END_COLUMN (5/15/24)
- Better names of files (utils?) (5/11/24)
- Restrict use of Google Resources/Clients using Singleton pattern instead of making multiple copies for no reason. (5/10/24)
  - Firestore ✅
  - Google Sheets ✅

# Recently Finished Bug Fixes

- Deprecate usage of `date`. Only use `datetime` for cross-compatibility (don't set time value if only requiring date portion). (5/15/24)
