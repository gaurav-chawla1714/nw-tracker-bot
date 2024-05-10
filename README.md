# How to run:

- `pip install -r requirements.txt`
- `python bot.py`

# Features

## In-Progress Features:

- Yahoo Finance API Integration
  -
- Integrate Google Firestore NoSQL Database as primary database
  - Sheets to be secondary storage for mobile viewing. However, all internal calculations will be queried to the Firestore database for ease of use.

## Upcoming Features:

- Updated help command to list out all of the existing commands
- Parse Fidelity account view xslx to update holdings manually

## Backlog:
- Date picking functionality (on hold)

# Bug Fixes

## In-Progress Fixes:
- N/A

## Upcoming fixes:

- Updating docstrings for existing methods

## Backlog:

- asyncio.TimeoutError does not properly disable buttons
- start date day restrictions need to be implemented
- end date year, month, day restrictions need to be implemented
