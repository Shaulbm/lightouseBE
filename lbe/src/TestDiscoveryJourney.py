# import sys
# sys.path.insert(0, 'C:\Dev\LighthouseBE\lbe\src')

from hashlib import new
from logging import error
import random
import uuid
import jsonpickle
import json
from generalData import UserData, UserContextData, Locale, Gender, UserRoles
import ExportJourney
from mongoLogic import MoovLogic
import userDiscoveryJourney as discovery

TESTS_NUMBER = 1

class reportResponseData:
    def __init__(self, id = "", idx = 0, questionId = "", motivationId = ""):
        self.id = id
        self.idx = idx,
        self.questionId = questionId
        self.motivationId = motivationId
        

class UserJourneyData:
    def __init__(self, id = "", userResponses = [], motivations = []):
        self.id = id
        self.userResponses = userResponses.copy()
        self.motivations = motivations.copy()

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject


def getQuestionByIdx (questions, questionBatchIdx):
    returnQuestion = None
    for currQuestion in questions:
        if currQuestion.batchIdx == questionBatchIdx:
            return currQuestion

    return None

def main():
    
    currTest = 0
    usersJourneysReport = []
    db = MoovLogic()

    while currTest < TESTS_NUMBER:
        #1. insert new user
        testPrefix = "T_" + str(uuid.uuid4())[:8] 
        userId = testPrefix + "_U_" + str(currTest)
        userMail = userId + "@gmail.com"
        newUser = UserData(id=userId, parentId= "" ,firstName="TestFN_" + userId, familyName="TestLN_"+userId, gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="OT002", role=UserRoles.MANAGER, mailAddress=userMail)
        userContext = UserContextData(newUser.id, newUser.firstName, newUser.familyName, newUser.gender, newUser.locale, newUser.isRTL)

        db.insertOrUpdateUser(newUser)

        currUserJourneyReport = UserJourneyData(id = userId)
        
        #2. start journey
        discovery.startUserJourney(userId)
        
        #3. get next ba    headlineRow = ["userId"]tch
        questionsBatch = discovery.getQuestionsBatch(userId=userId, userContext=userContext) 
        
        questionsSetDict = {}

        #4. while next batch is not empty

        while len(questionsBatch) > 0:
            currQuestionIdx = 0
            sortedQuestionsIdx = [x.batchIdx for x in questionsBatch]
            sortedQuestionsIdx.sort()
            lastSetId = ""
            lastResponseId = ""
            while currQuestionIdx < len(questionsBatch):
                # get curr idx, compare to last set id to know whther to remove the response from possible answers
                currQuestion = getQuestionByIdx(questionsBatch, sortedQuestionsIdx[currQuestionIdx])

                if currQuestion.batchId !="B99" and currQuestion.batchId != "B100":
                     # this is a regular question (not tail or motivation gap) 
                    currQuestionPossibleResponses = []
                    for currResponse in currQuestion.possibleResponses:
                        if currQuestion.setId != lastSetId or (currQuestion.setId == lastSetId and currResponse.dependency != lastResponseId):
                            #this is a part of a set, we need to consider the last answer
                            currQuestionPossibleResponses.append(currResponse)
                                               
                    selectedIndex = random.randint(0,len(currQuestionPossibleResponses)-1)

                    selectedResponse = currQuestionPossibleResponses[selectedIndex]
                    lastResponseId = selectedResponse.id

                    if currQuestion.setId != lastSetId:
                        #this is a new set
                        lastSetId = currQuestion.setId

                    discovery.setUserResponse(userId=userId, questionId=currQuestion.id, responseId=selectedResponse.id, userContext=userContext)
                    currUserResponseReport = reportResponseData()
                    currUserResponseReport.questionId = currQuestion.id
                    currUserResponseReport.id = selectedResponse.id
                    currUserResponseReport.idx = selectedResponse.idx
                    currUserResponseReport.motivationId = selectedResponse.motivationId

                    currUserJourneyReport.userResponses.append (currUserResponseReport)
                elif currQuestion.batchId == 'B99':
                    #this is tail resolution question
                    responsesList = random.sample(currQuestion.possibleResponses, currQuestion.userResponsesNo)
                    
                    discovery.setUserMultipleResponses(userId=userId, questionId=currQuestion.id, responses=responsesList)

                    for currResponseData in responsesList:
                        currUserResponseReport = reportResponseData()
                        currUserResponseReport.questionId = currQuestion.id
                        currUserResponseReport.id = currResponseData.id
                        currUserResponseReport.idx = currResponseData.idx
                        currUserResponseReport.motivationId = currResponseData.motivationId

                        currUserJourneyReport.userResponses.append (currUserResponseReport)
                elif currQuestion.batchId == 'B100':
                    #this is motivation gap question
                    motivationGapScore = random.randint(1, 5)
                    discovery.setUserScoredResponse(userId=userId, questionId=currQuestion.id, score=motivationGapScore, userContext=userContext)
                    
                    currUserResponseReport = reportResponseData()
                    currUserResponseReport.questionId = currQuestion.id
                    currUserResponseReport.id = str(motivationGapScore)
                    currUserResponseReport.idx = "0"
                    currUserResponseReport.motivationId = currQuestion.motivationId

                    currUserJourneyReport.userResponses.append (currUserResponseReport)
                
                currQuestionIdx +=1

            questionsBatch = discovery.getQuestionsBatch(userId= userId, userContext=userContext)
            
        currentUser = db.getUser(userId)
        currUserJourneyReport.motivations = currentUser.motivations
        usersJourneysReport.append(currUserJourneyReport)
        currTest +=1

        print ("Current text Iteration ", currTest)
    
    exportDataToExcel(usersJourneysReport)

def exportDataToExcel(usersJourneysReport):
    #Open Excel File

    ExportJourney.writeJourneyTestReport(usersJourneysReport)

    # #Write Data
    # for currJourneyReport in usersJourneysReport:
    #     print (currJourneyReport)

if __name__ == '__main__':
    main()