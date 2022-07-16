from __future__ import print_function
from cgitb import text
from hashlib import new
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from issuesData import IssueData, RelatedMotivationData, SubjectData, ConflictData
from generalData import TextData
from moovLogic import MoovLogic

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
ISSUES_SPREADSHEET_ID = '1igInUX3D9zOeSc29QJ9o3hafMvyrWdbnv9-0r5V6Qj4'
GENERAL_RANGE_NAME = 'General!A1:E4'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'c:\\Dev\\LighthouseBE\\Data\\client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ISSUES_SPREADSHEET_ID,
                                range=GENERAL_RANGE_NAME).execute()
    textsValues = result.get('values', [])

    if not textsValues:
        print('No data found.')
    else:
        keysRow = textsValues[0]
        #skip the first row (keys row)
        for currRow in textsValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currText = dict(zip_iterator)

            #create motivations
            insertText(textDataDict=currText)

def insertText(textDataDict):
    print ('importing System Text ', textDataDict["id"])
    dbInstance = MoovLogic()
    db = dbInstance.getDatabase().getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    currentTextData = TextData(parentId=textDataDict["parentId"], Id=textDataDict["id"], contentText=textDataDict["text <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(parentId=textDataDict["parentId"], Id=textDataDict["id"], contentText=textDataDict["text <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(parentId=textDataDict["parentId"], Id=textDataDict["id"], contentText=textDataDict["text <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

if __name__ == '__main__':
    main()