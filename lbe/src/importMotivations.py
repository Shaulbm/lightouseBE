from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from motivationsData import InsightTypeData, MotivationInsightData, MotivationData
from generalData import TextData
from moovLogic import MoovLogic

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1JBx_pa3Em_uJBn9LJVcT6TJ9nfiPp8zl1X86tZ-GjEE'
SAMPLE_RANGE_NAME = 'MotivationsDetails!A1:R31'
INSIGHTS_RANGE_NAME = 'MotivationsInsights!A1:K391'
INSIGHTS_TYPES_RANGE_NAME = 'Insights!A1:E14'

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
    motivationsValues = result.get('values', [])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=INSIGHTS_RANGE_NAME).execute()
    insightsValues = result.get('values', [])

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=INSIGHTS_TYPES_RANGE_NAME).execute()
    insightsTypesValues = result.get('values', [])

    if not insightsValues or not motivationsValues or not insightsTypesValues:
        print('No data found.')
        return

    reponseKeyRow = insightsTypesValues[0]
    for currRow in insightsTypesValues[1:]:
        zip_iterator = zip(reponseKeyRow, currRow)
        currInsightType = dict(zip_iterator)

        insertInsightType(currInsightType)

    reponseKeyRow = insightsValues[0]
    for currRow in insightsValues[1:]:
        zip_iterator = zip(reponseKeyRow, currRow)
        currInsight = dict(zip_iterator)

        insertMotivationInsight(currInsight)

    print('Name, Major:')
    keysRow = motivationsValues[0]
    #skip the first row (keys row)
    for currRow in motivationsValues[1:]:
        zip_iterator = zip (keysRow, currRow)
        currMotivation = dict(zip_iterator)
    
        #create motivation
        insertMotivation(currMotivation)

def insertMotivation(motivationDataDict):
    dbInstance = MoovLogic()
    db = dbInstance.getDatabase().getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newMotivation = MotivationData()
    newMotivation.id = motivationDataDict["id"]
    newMotivation.name = newMotivation.id + "_1"
    newMotivation.shortDescription = newMotivation.id + "_2"
    newMotivation.longDescription = newMotivation.id + "_3"
    newMotivation.tailResolution = newMotivation.id + "_4"
    newMotivation.longDescriptionPlural = newMotivation.id + "_5"
    newMotivation.imageUrl = motivationDataDict["imageUrl"]
    newMotivation.color =motivationDataDict["color"]

    currentTextData = TextData(newMotivation.id, newMotivation.name, motivationDataDict["name <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.name, motivationDataDict["name <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.name, motivationDataDict["name <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.shortDescription, motivationDataDict["short description <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.shortDescription, motivationDataDict["short description <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.shortDescription, motivationDataDict["short description <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescription, motivationDataDict["long description <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescription, motivationDataDict["long description <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescription, motivationDataDict["long description <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescriptionPlural, motivationDataDict["long description plural <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescriptionPlural, motivationDataDict["long description plural <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.longDescriptionPlural, motivationDataDict["long description plural <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.tailResolution, motivationDataDict["tail resolution <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.tailResolution, motivationDataDict["tail resolution <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData)

    currentTextData = TextData(newMotivation.id, newMotivation.tailResolution, motivationDataDict["tail resolution <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData)

    dbInstance.insertOrUpdateMotivation(newMotivation)

def insertMotivationInsight(insightDataDict):
    dbInstance = MoovLogic()
    db = dbInstance.getDatabase().getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    insightDetails = MotivationInsightData()
    insightDetails.id = insightDataDict["id"]
    insightDetails.motivationId = insightDataDict["motivationId"]
    insightDetails.insightId = insightDataDict["insightId"]
    insightDetails.type = int(insightDataDict["type"])
    insightDetails.shortDescription = insightDetails.id + "_1"
    insightDetails.longDescription = insightDetails.id + "_2"

    currentTextData = TextData(insightDetails.id, insightDetails.shortDescription, insightDataDict["shortDescription <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightDetails.id, insightDetails.shortDescription, insightDataDict["shortDescription <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightDetails.id, insightDetails.shortDescription, insightDataDict["shortDescription <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightDetails.id, insightDetails.longDescription, insightDataDict["longDescription <<en>>"].replace('•', '\n•'))
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightDetails.id, insightDetails.longDescription, insightDataDict["longDescription <<he_ma>>"].replace('•', '\n•'))
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightDetails.id, insightDetails.longDescription, insightDataDict["longDescription <<he_fe>>"].replace('•', '\n•'))
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData) 

    dbInstance.insertOrUpdateMotivationInsight(insightDetails=insightDetails)

def insertInsightType(insightTypeDataDict):
    dbInstance = MoovLogic()
    db = dbInstance.getDatabase().getDatabase()

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    insightTypeDetails =InsightTypeData()
    insightTypeDetails.id = insightTypeDataDict["id"]
    insightTypeDetails.type = int(insightTypeDataDict["type"])
    insightTypeDetails.text = insightTypeDetails.id + "_1"

    currentTextData = TextData(insightTypeDetails.id, insightTypeDetails.text, insightTypeDataDict["text <<en>>"])
    dbInstance.insertOrUpdateText(eng_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightTypeDetails.id, insightTypeDetails.text, insightTypeDataDict["text <<he_ma>>"])
    dbInstance.insertOrUpdateText(heb_ma_LocaleCollection, currentTextData) 

    currentTextData = TextData(insightTypeDetails.id, insightTypeDetails.text, insightTypeDataDict["text <<he_fe>>"])
    dbInstance.insertOrUpdateText(heb_fe_LocaleCollection, currentTextData) 

    dbInstance.insertOrUpdateInsightType (insightTypeDetails)

if __name__ == '__main__':
    main()