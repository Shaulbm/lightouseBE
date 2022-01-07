from __future__ import print_function
from hashlib import new
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from questionsData import QuestionData, ResponseData
import mongoDB
from generalData import TextData
from TestDiscoveryJourney import UserJourneyData, reportResponseData

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1YmVZQfqm0Fp9gXoEVQDntEaEtCET1ZiVNreCPvIyFKc'
RESULTS_RANGE_NAME = 'Results'

def writeJourneyTestReport(journeysReport):
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
    sheets = service.spreadsheets()

    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=QUESTIONS_RANGE_NAME).execute()
    # questionsValues = result.get('values', [])
    rows = []
    # rows.append(["xest1", "xest2"])
    # rows.append(["test1","test2"])

    # response_date = sheets.values().update(
    #     spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #     valueInputOption='RAW',
    #     range=RESULTS_RANGE_NAME,
    #     body=dict(
    #         majorDimension='ROWS',
    #         values=rows)
    # ).execute()

    #get first journey and add all the questions to the row, add also Q99_1...Q99_10
    headlineRow = ["userId"]

    for currResponse in journeysReport[0].userResponses:
        if "Q999" not in currResponse.questionId:
            headlineRow.append(currResponse.questionId)            

    idx = 1
    while idx < 6:
        headlineRow.append("Q999_" + str(idx))
        idx += 1

    idx = 1
    while idx < 6:
        headlineRow.append("Motivation " + str(idx))
        idx += 1

    rows.append(headlineRow)

    #write rows
    
    for currJourney in journeysReport:
        newRow = []
        newRow.append(currJourney.id)
        for currResponse in currJourney.userResponses:
            if "Q999" not in currResponse.questionId:
                newRow.append(currResponse.idx)
            else:
                newRow.append(currResponse.motivationId)

        #missing Cells 60 Questions + max 5 for tail + userId
        missingIdx = 66 - len(newRow)
        while missingIdx > 0:
            newRow.append("")
            missingIdx -= 1

        for currMotivation in currJourney.motivations:
            newRow.append(currMotivation)

        rows.append(newRow)

    response_date = sheets.values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        valueInputOption='RAW',
        range=RESULTS_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=rows)
    ).execute()
    print('Sheet successfully Updated')

    #writeRow