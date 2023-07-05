import os.path

from googleapiclient.discovery import build
from google.oauth2 import service_account
from base.base_handlers_sheets import get_orders_info, get_users_info

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def add_all_users_to_sheet():
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = 'users_storage'
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    pull = get_users_info()
    print (pull)
    body = {'values': pull}

    result = service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(result)


def add_string():
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = 'orders_storage'
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    values = get_orders_info()
    body = {
        "values": values
    }
    print(values)
    # Append the values to the sheet
    result = service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(result)

async def add_last_string(values:[()], sheet:str):
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = sheet
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    body = {
        "values": values
    }
    print(body)
    # Append the values to the sheet
    service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
        ).execute()

def add_last_strings_to_basket(values:[()], sheet:str):
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = sheet
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

    # Construct a new list of values that includes the image formula

    body = {
        "values": values
    }

    # Append the values to the sheet, specifying that the data should be interpreted as a formula
    service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()


