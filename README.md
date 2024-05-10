# How to run:

- `pip install -r requirements.txt`
- `python bot.py`

# Features

## In-Progress Features:

- Integrate Google Firestore NoSQL Database as primary database
  - Sheets to be secondary storage for mobile viewing. However, all internal calculations will be queried to the Firestore database for ease of use.
  - All existing data needs to be migrated over.
- Restrict use of Google Resources/Clients using Singleton pattern instead of making multiple copies for no reason.

## Upcoming Features:
- Yahoo Finance API Integration
  - real-time pricing data for real-time estimated nw calculations.
- Updated help command to list out all of the existing commands
  - Right now, the only ones is status
- Parse Fidelity account view xslx to update holdings. Use pandas to parse excel file.
- Better names of files (utils?)
- Integrate custom exceptions more, including messages. Integrate on read commands as well.

## Backlog:
- Date picking functionality
    - start date day restrictions need to be implemented
    - end date year, month, day restrictions need to be implemented
    - once dates are collected, need to do actual queries

# Bug Fixes

## In-Progress Fixes:
- N/A

## Upcoming fixes:

- Updating docstrings for existing methods

## Backlog:
- Date picking functionality bugs
    - asyncio.TimeoutError does not properly disable buttons
