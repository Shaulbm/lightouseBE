from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from moovData import MoovData
import mongoDB
from motivationsData import MotivationData
from generalData import TextData

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1eBZQ8wmTyn3DVDfqHrtRJ3hoL056hUnrlPh3q9CuYok'
SAMPLE_RANGE_NAME = 'MoovsDetails!A1:O4'

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
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        keysRow = values[0]
        #skip the first row (keys row)
        for currRow in values[1:]:
            zip_iterator = zip (keysRow, currRow)
            currMoov = dict(zip_iterator)

            #create motivations
            insertMoov(currMoov)

def insertMoov(moovDataDict):
    dbInstance = mongoDB.moovDBInstance()
    db = dbInstance.getDatabase()
    moovsCollection = db["moovs"]

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newMoov = MoovData()
    newMoov.id = moovDataDict["id"]
    newMoov.issueId = moovDataDict["issueId"]
    newMoov.motivationId = moovDataDict["motivationId"]
    newMoov.score = int(moovDataDict["score"])
    newMoov.image = moovDataDict["image"]
    newMoov.name = newMoov.id + "_1"
    newMoov.description = newMoov.id + "_2"
    newMoov.howTo = newMoov.id + "_3"
    newMoov.contributorId = moovDataDict["contributorId"]

    currentTextData = TextData(newMoov.id, newMoov.name, moovDataDict["name <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.name, moovDataDict["name <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.name, moovDataDict["name <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.description, moovDataDict["description <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.description, moovDataDict["description <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.description, moovDataDict["description <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.howTo, moovDataDict["howTo <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.howTo, moovDataDict["howTo <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMoov.id, newMoov.howTo, moovDataDict["howTo <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    dbInstance.insertOrUpdateMoov(newMoov)

if __name__ == '__main__':
    main()