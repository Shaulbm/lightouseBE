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

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1YOdX9KDiPrM21-olNz1Mgl5lfMQPyMz1J4LvVRQ6iow'
QUESTIONS_RANGE_NAME = 'Questions!A1:H61'
RESPONSES_RANGE_NAME = 'Responses!A1:H241'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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
                                range=QUESTIONS_RANGE_NAME).execute()
    questionsValues = result.get('values', [])
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=RESPONSES_RANGE_NAME).execute()
    responsesValues = result.get('values', [])

    if not questionsValues or not responsesValues:
        print('No data found.')
    else:
        #change responses to array of dictionaries
        responsesArray = []
        reponseKeyRow = responsesValues[0]
        for currRow in responsesValues[1:]:
            zip_iterator = zip(reponseKeyRow, currRow)
            currResponse = dict(zip_iterator)
            responsesArray.append(currResponse.copy())

        keysRow = questionsValues[0]
        #skip the first row (keys row)
        for currRow in questionsValues[1:]:
            zip_iterator = zip (keysRow, currRow)
            currQuestion = dict(zip_iterator)

            #select the reponses for this question

            currResponses = [r.copy() for r in responsesArray if r["questionId"] == currQuestion["id"]]

            #create motivations
            insertQuestion(currQuestion, currResponses)

def insertQuestion(questionsDataDict, responsesDataDictArray):
    dbInstance = mongoDB.moovDBInstance()
    db = dbInstance.getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newQuestion = QuestionData()
    newQuestion.id = questionsDataDict["id"]
    newQuestion.batchId = questionsDataDict["batchId"]
    newQuestion.batchIdx = questionsDataDict["batchIdx"]
    newQuestion.setId = questionsDataDict["setId"]
    newQuestion.setIdx = questionsDataDict["setIdx"]
    newQuestion.questionText = newQuestion.id + "_1"
    newQuestion.possibleResponses = []

    currentTextData = TextData(newQuestion.id, newQuestion.questionText, questionsDataDict["question_text <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newQuestion.id, newQuestion.questionText, questionsDataDict["question_text <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newQuestion.id, newQuestion.questionText, questionsDataDict["question_text <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    for currResponseData in responsesDataDictArray:
        newReponse = ResponseData()
        newReponse.id = currResponseData["id"]
        newReponse.idx = currResponseData["idx"]
        newReponse.questionId = currResponseData["questionId"]
        newReponse.motivationId = currResponseData["motivationId"]
        newReponse.motivationScore = currResponseData["motivationScore"]
        newReponse.responseText = newReponse.id + "_1"

        currentTextData = TextData(newReponse.id, newReponse.responseText, currResponseData["responseText <<en>>"])
        dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

        currentTextData = TextData(newReponse.id, newReponse.responseText, currResponseData["responseText <<he_fe>>"])
        dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

        currentTextData = TextData(newReponse.id, newReponse.responseText, currResponseData["responseText <<he_ma>>"])
        dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

        newQuestion.possibleResponses.append(newReponse)

    dbInstance.insertOrUpdateQuestion(newQuestion)

if __name__ == '__main__':
    main()