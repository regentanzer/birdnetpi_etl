import sqlite3
import shutil
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants
DATABASE_PATH = '/home/[BirdNET Username]/BirdNET-Pi/scripts/birds.db'
TEMP_DATABASE_PATH = '/home/[BirdNET Username]/BirdNET-Pi/scripts/temp_birds.db'
GOOGLE_SHEET_NAME = '[Name of Google Workbook]'
CREDS_JSON_PATH = '/home/[BirdNET Username]/venv/google_sheets_credentials.json'

# Create a temporary copy of the database
shutil.copy(DATABASE_PATH, TEMP_DATABASE_PATH)

# Connect to the temporary database
conn = sqlite3.connect(TEMP_DATABASE_PATH)
cursor = conn.cursor()

# Define the scope for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Authenticate and connect to Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON_PATH, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open(GOOGLE_SHEET_NAME).[Name of individual sheet]

# Fetch all existing data from the Google Sheet
existing_data = sheet.get_all_records()

# Create a set of existing bird IDs to avoid duplicates
existing_ids = {record['ID'] for record in existing_data}  

# Query new data from the temporary database
cursor.execute("SELECT CONCAT(SUBSTR(time,1,2),Com_Name) AS id, Date, Week, SUBSTR(time,1,2) AS Hour, Com_Name AS Common_Name, COUNT(DISTINCT File_Name) AS Detections FROM detections GROUP BY 1,2,3,4,5")
new_records = cursor.fetchall()

# Prepare data to upload
data_to_upload = []

for record in new_records:
    bird_id = record[0]  
    if bird_id not in existing_ids:
        data_to_upload.append(record)

# If there's new data to upload
if data_to_upload:
    # Prepare to insert new records into the Google Sheet
    for row in data_to_upload:
        sheet.append_row(row)

# Cleanup
cursor.close()
conn.close()
