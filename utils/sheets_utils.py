import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# Read all records into a list of dicts
# data = sheet.get_all_records()

# # Convert to pandas DataFrame
# df = pd.DataFrame(data)

# sheet.append_row([2,"das","ddwa","wda","dadsd","dsada"])

def connectToSheets():
    scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def sheet():
    client=connectToSheets()
    sheet=client.open("Ticket Details").sheet1
    return sheet


def insertRecord(row):
    client=connectToSheets()
    sheet = client.open("Ticket Details").sheet1  # first worksheet
    sheet.append_row(row)
    sheet

def get_row_number_by_ticket_id(ticket_id):
    client = connectToSheets()
    sheet = client.open("Ticket Details").sheet1

    # Ensure ticket_id is a string and strip spaces
    ticket_id = str(ticket_id).strip()

    # Get all ticket IDs from column A
    ticket_ids = [str(tid).strip() for tid in sheet.col_values(1)]

    try:
        row_number = ticket_ids.index(ticket_id) + 1  # +1 for 1-based indexing
        return row_number
    except ValueError:
        return None  # ticket_id not found

def updateTicketStatusAndSatisfaction(ticket_id, ticket_status, ticket_satisfaction):
    client = connectToSheets()
    sheet = client.open("Ticket Details").sheet1

    # Find row number
    row_number = get_row_number_by_ticket_id(ticket_id)
    if row_number is None:
        print(f"Ticket ID {ticket_id} not found!")
        return

    # Update ticket_status (column G) and ticket_satisfaction (column H)
    sheet.update_cell(row_number, 6, ticket_status)        # Column G = 7
    sheet.update_cell(row_number, 8, ticket_satisfaction)  # Column H = 8

    print(f"Row {row_number} updated successfully: status={ticket_status}, satisfaction={ticket_satisfaction}")

# print(df.head())
def get_data():
    client = connectToSheets()
    sheet = client.open("Ticket Details").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

