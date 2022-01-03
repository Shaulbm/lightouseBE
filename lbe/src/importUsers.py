from __future__ import print_function
from hashlib import new
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pydantic.errors import NoneIsAllowedError
from generalData import UserData
import mongoDB

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
USERS_SPREADSHEET_ID = '11AgEYCS-9SsBAxDqpG8q_1pNrmr-BFJyZbUNTM0AOe8'
USERS_RANGE_NAME = 'Users!A1:J7'

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
    result = sheet.values().get(spreadsheetId=USERS_SPREADSHEET_ID,
                                range=USERS_RANGE_NAME).execute()
    usersValues = result.get('values', [])

    if not usersValues:
        print ('No subjects Data Found')
    else:
        keysRow = usersValues[0]
        for currRow in usersValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currSubject = dict(zip_iterator)

            #create motivations
            insertUser(userDataDict=currSubject)        

def insertUser(userDataDict):
    dbInstance = mongoDB.MoovDBInstance()
    db = dbInstance.getDatabase()

    newUser = UserData()
    newUser.id = userDataDict["id"]
    newUser.firstName = userDataDict["firstName"]
    newUser.familyName = userDataDict["lastName"]
    newUser.mailAddress = userDataDict["mail"]
    newUser.orgId = userDataDict["orgId"]
    newUser.parentId = userDataDict["parentId"]
    newUser.role = int(userDataDict["role"])
    newUser.gender = int(userDataDict["gender"])
    newUser.locale = userDataDict["locale"]
    
    poiList = []
    if "personsOfInterest" in userDataDict:
        if (userDataDict["personsOfInterest"] != ""):
            poiList = str(userDataDict["personsOfInterest"]).split(',').copy()
            
    newUser.personsOfInterest = poiList.copy()

    dbInstance.insertOrUpdateUser(newUser)

if __name__ == '__main__':
    main()