from __future__ import print_function
from hashlib import new
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from issuesData import IssueData, RelatedMotivationData, SubjectData, ConflictData
import mongoDB
from generalData import TextData

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
ISSUES_SPREADSHEET_ID = '1c68_oJr28b6USdkj3CW5h9KaXvLKpB5iCACJoKygEs0'
ISSUES_RANGE_NAME = 'Issues!A1:K10'
SUBJECTS_RANGE_NAME = 'Subjects!A1:G4'
RESOLVING_MOTIVATIONS_RANGE_NAME = 'IssueResolvingMotivations!A1:J22'
CONTRIBUTING_MOTIVATIONS_RANGE_NAME = 'IssueContributingMotivations!A1:J19'
CONFLICTS_RANGE_NAME='Conflicts!A1:H6'

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
                                range=ISSUES_RANGE_NAME).execute()
    issuesValues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=ISSUES_SPREADSHEET_ID,
                                range=RESOLVING_MOTIVATIONS_RANGE_NAME).execute()
    resolvingMotivationsValues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=ISSUES_SPREADSHEET_ID,
                                range=CONTRIBUTING_MOTIVATIONS_RANGE_NAME).execute()
    conributingMotivationsValues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=ISSUES_SPREADSHEET_ID,
                                range=SUBJECTS_RANGE_NAME).execute()
    subjectsValues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=ISSUES_SPREADSHEET_ID,
                                range=CONFLICTS_RANGE_NAME).execute()
    conflictValues = result.get('values', [])
   

    if not subjectsValues:
        print ('No subjects Data Found')
    else:
        keysRow = subjectsValues[0]
        for currRow in subjectsValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currSubject = dict(zip_iterator)

            #create motivations
            insertSubject(subjectDataDict=currSubject)        

    if not conflictValues:
        print ('No subjects Data Found')
    else:
        keysRow = conflictValues[0]
        for currRow in conflictValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currConflict = dict(zip_iterator)

            #create motivations
            insertConflict(conflictDataDict=currConflict)  

    if not issuesValues or not resolvingMotivationsValues or not conributingMotivationsValues:
        print('No data found.')
    else:
        #change responses to array of dictionaries
        resolvingMotivationsArray = []
        resolvingMotivationsKeyRow = resolvingMotivationsValues[0]
        for currRow in resolvingMotivationsValues[1:]:
            zip_iterator = zip(resolvingMotivationsKeyRow, currRow)
            currResolvingMotivation = dict(zip_iterator)
            resolvingMotivationsArray.append(currResolvingMotivation.copy())

        contributingMotivationsArray = []
        contributingMotivationsKeyRow = conributingMotivationsValues[0]
        for currRow in conributingMotivationsValues[1:]:
            zip_iterator = zip(contributingMotivationsKeyRow, currRow)
            currContributingMotivation = dict(zip_iterator)
            contributingMotivationsArray.append(currContributingMotivation.copy())

        keysRow = issuesValues[0]
        #skip the first row (keys row)
        for currRow in issuesValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currIssue = dict(zip_iterator)

            #select the motivations for this issue

            currResolvingMotivations = [r.copy() for r in resolvingMotivationsArray if r["issueId"] == currIssue["id"]]
            currContributingMotivations = [r.copy() for r in contributingMotivationsArray if r["issueId"] == currIssue["id"]]

            #create motivations
            insertIssue(issueDataDict=currIssue, resolvingMotivationsDictArray=currResolvingMotivations, contributingMotivationsDictArray=currContributingMotivations)

def insertSubject(subjectDataDict):
    dbInstance = mongoDB.moovDBInstance()
    db = dbInstance.getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newSubject = SubjectData()
    newSubject.id = subjectDataDict["id"]
    newSubject.name = newSubject.id + "_1"
    newSubject.description = newSubject.id + "_2"
 
    currentTextData = TextData(newSubject.id, newSubject.name, subjectDataDict["name <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newSubject.id, newSubject.name, subjectDataDict["name <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newSubject.id, newSubject.name, subjectDataDict["name <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newSubject.id, newSubject.description, subjectDataDict["description <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData) 

    currentTextData = TextData(newSubject.id, newSubject.description, subjectDataDict["description <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newSubject.id, newSubject.description, subjectDataDict["description <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    dbInstance.insertOrUpdateSubject(newSubject)

def insertConflict (conflictDataDict):
    dbInstance = mongoDB.moovDBInstance()
    db = dbInstance.getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newConflict = ConflictData()
    newConflict.id = conflictDataDict["id"]
    newConflict.motivationId = conflictDataDict["motivationId"]
    newConflict.motivationCounterpartId = conflictDataDict["motivationCounterpartId"]
    newConflict.score = int(conflictDataDict["score"])
    newConflict.relationType =  int(conflictDataDict["relationType"])
    newConflict.description = newConflict.id + "_1"
 
    currentTextData = TextData(newConflict.id, newConflict.description, conflictDataDict["description <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newConflict.id, newConflict.description, conflictDataDict["description <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newConflict.id, newConflict.description, conflictDataDict["description <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    dbInstance.insertOrUpdateConflict(newConflict)


def insertIssue(issueDataDict, resolvingMotivationsDictArray, contributingMotivationsDictArray):
    dbInstance = mongoDB.moovDBInstance()
    db = dbInstance.getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newIssue = IssueData()
    newIssue.id = issueDataDict["id"]
    newIssue.subjectId = issueDataDict["subjectId"]
    newIssue.name = newIssue.id + "_1"
    newIssue.shortDescription = newIssue.id + "_2"
    newIssue.longDescription = newIssue.id + "_3"
    newIssue.contributingMotivations = []
    newIssue.resolvingMotivations = []

    currentTextData = TextData(newIssue.id, newIssue.name, issueDataDict["name <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.name, issueDataDict["name <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.name, issueDataDict["name <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.shortDescription, issueDataDict["shortDescription <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.shortDescription, issueDataDict["shortDescription <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.shortDescription, issueDataDict["shortDescription <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.longDescription, issueDataDict["longDescription <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.longDescription, issueDataDict["longDescription <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newIssue.id, newIssue.longDescription, issueDataDict["longDescription <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    for currResolvingMotivations in resolvingMotivationsDictArray:
        newResolvingMotivation = RelatedMotivationData()
        newResolvingMotivation.id = currResolvingMotivations["id"]
        newResolvingMotivation.issueId = currResolvingMotivations["issueId"]
        newResolvingMotivation.motivationId = currResolvingMotivations["motivationId"]
        newResolvingMotivation.impact = int(currResolvingMotivations["impact"])
        newResolvingMotivation.text = newResolvingMotivation.id + "_1"
        newResolvingMotivation.moovExplanation = newResolvingMotivation.id + "_2"

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.text, currResolvingMotivations["text <<en>>"])
        dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.text, currResolvingMotivations["text <<he_fe>>"])
        dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.text, currResolvingMotivations["text <<he_ma>>"])
        dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.moovExplanation, currResolvingMotivations["moovExplanation <<en>>"])
        dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.moovExplanation, currResolvingMotivations["moovExplanation <<he_fe>>"])
        dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

        currentTextData = TextData(newResolvingMotivation.id, newResolvingMotivation.moovExplanation, currResolvingMotivations["moovExplanation <<he_ma>>"])
        dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

        newIssue.resolvingMotivations.append(newResolvingMotivation)

    for currContributingMotivations in contributingMotivationsDictArray:
        newContributingMotivation = RelatedMotivationData()
        newContributingMotivation.id = currContributingMotivations["id"]
        newContributingMotivation.issueId = currContributingMotivations["issueId"]
        newContributingMotivation.motivationId = currContributingMotivations["motivationId"]
        newContributingMotivation.impact = int(currContributingMotivations["impact"])
        newContributingMotivation.text = newContributingMotivation.id + "_1"
        newContributingMotivation.moovExplanation = newContributingMotivation.id + "_2"

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.text, currContributingMotivations["text <<en>>"])
        dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.text, currContributingMotivations["text <<he_fe>>"])
        dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.text, currContributingMotivations["text <<he_ma>>"])
        dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.moovExplanation, currContributingMotivations["moovExplanation <<en>>"])
        dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.moovExplanation, currContributingMotivations["moovExplanation <<he_fe>>"])
        dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

        currentTextData = TextData(newContributingMotivation.id, newContributingMotivation.moovExplanation, currContributingMotivations["moovExplanation <<he_ma>>"])
        dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)
        newIssue.contributingMotivations.append(newContributingMotivation)

    dbInstance.insertOrUpdateIssue(newIssue)

if __name__ == '__main__':
    main()