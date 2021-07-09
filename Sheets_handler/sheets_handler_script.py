# [START sheets_quickstart]
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1OjaPuWAerkMlQiI3kZRvy6jaSDoGEQmnKuRi4aSOj9A'
SAMPLE_RANGE_NAME = [
    'Users',
    'Issues',
    'Training',
    'Challenges',
    'Courses',
    'Lessons'
]
class g_sheets():
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('sheets', 'v4', credentials=creds)

    def read_all_values(self):
        self.sheet_data = {}
        for range_name in SAMPLE_RANGE_NAME:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_name).execute()
            rows = result.get('values', [])
            temp_record = {}
            rows_data = []
            for i in range(2,len(rows)):
                for j,item in enumerate(rows[1]):
                    temp_record.update({
                        item : rows[i][j]
                    })
                rows_data.append(temp_record)
            self.sheet_data.update({
                range_name : rows_data
            })
            print('{0} rows retrieved.'.format(len(rows)))
    # def update_jira_values(self, values_to_write):
    #     # Call the Sheets API
    #     sheet = self.service.spreadsheets()
    #     result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                                 range=SAMPLE_RANGE_NAME).execute()
    #     values = result.get('values', [])
    #     row_to_add = values.__len__()
    #     range = SAMPLE_RANGE_NAME + '!A{}:K'.format(row_to_add + 1)
    #     body = {
    #         'values': values_to_write
    #     }
    #     result = self.service.spreadsheets().values().update(
    #         spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #         range=range,
    #         valueInputOption='RAW',
    #         body=body).execute()
    #     print('{0} cells updated.'.format(result.get('updatedCells')))