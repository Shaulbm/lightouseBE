from __future__ import print_function
from hashlib import new
from multiprocessing import parent_process
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from pydantic.errors import NoneIsAllowedError
from generalData import UserData
from generalData import Locale
from moovLogic import MoovLogic

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
USERS_SPREADSHEET_ID = '1dprvs72UP0mn8mAKWqwHWaCAm2V62_nx4IS76BR-su0'
USERS_RANGE_NAME = 'O_org1_1!A1:G4'

orphanedEmployees = {}

def importUsers(spreadsheetId = USERS_SPREADSHEET_ID, dataRange=USERS_RANGE_NAME):
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
    result = sheet.values().get(spreadsheetId=spreadsheetId,
                                range=dataRange).execute()
    usersValues = result.get('values', [])

    usersCount = 0

    if not usersValues:
        print ('No subjects Data Found')
    else:
        keysRow = usersValues[0]
        for currRow in usersValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currSubject = dict(zip_iterator)

            #create motivations
            insertUser(userDataDict=currSubject)   
            usersCount += 1     

    dbInstance = MoovLogic()

    for key, value in orphanedEmployees.items():
        parnentDetails = dbInstance.getUserByMail(value)

        if (parnentDetails is None):
            # trying to add a user whose parent is not there
            print ("parent mail was mentioned but not added userMail {0} ParentMail {1}", key, value)
        else:
            userDetails = dbInstance.getUserByMail(key)
            if (userDetails):
                # user and parent details shoud be in the DB - update user
                userDetails.parentId = parnentDetails.id

                print ('updating orphaned user {0}', userDetails.mailAddress)
                dbInstance.insertOrUpdateUser(userDetails)

    return usersCount

def insertUser(userDataDict):
    print ('imported user {0}', userDataDict["mailAddress"])

    dbInstance = MoovLogic()
    db = dbInstance.getDatabase()

    parentMailAddress = userDataDict["parentMail"]
    parentId = ""
    if (parentMailAddress != ""):
        parentData = dbInstance.getUserByMail(parentMailAddress)    
        if (parentData is None):
            # parent was not added to the DB
            orphanedEmployees[userDataDict["mailAddress"]] = parentMailAddress
        else:
            # parent alredy added
            parentId = parentData.id
            
    dbInstance.createUser(notifyNewUser=True, parentId=parentId, firstName=userDataDict["firstName"], familyName=userDataDict["lastName"], gender=int(userDataDict["gender"]), locale=Locale.LOCALE_HE_IL, orgId=userDataDict["orgId"], role = int(userDataDict["role"]), mailAddress=userDataDict["mailAddress"])

if __name__ == '__main__':
    importUsers()