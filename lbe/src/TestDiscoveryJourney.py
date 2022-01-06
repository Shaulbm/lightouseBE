# import sys
# sys.path.insert(0, 'C:\Dev\LighthouseBE\lbe\src')

import random
import gateway
import uuid
import jsonpickle
import json
from generalData import UserData
import ExportJourney

TESTS_NUMBER = 250

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


def getQuestionByIdx (questions, questionIdx):
    returnQuestion = None
    for currQuestion in questions:
        if currQuestion.batchIdx == questionIdx:
            return currQuestion

    return None

def main():
    
    currTest = 0
    usersJourneysReport = []
    while currTest < TESTS_NUMBER:
        #1. insert new user
        testPrefix = "T_" + str(uuid.uuid4())[:8] 
        userId = testPrefix + "_U_" + str(currTest)
        userMail = userId + "@gmail.com"
        gateway.add_or_update_user(userId, userMail)

        currUserJourneyReport = UserJourneyData(id = userId)
        
        #2. start journey
        gateway.start_user_journey(userId)
        
        #3. get next ba    headlineRow = ["userId"]tch
        questionsBatch = gateway.get_next_questions_batch(userId, 1) 
        
        questionsSetDict = {}

        #4. while next batch is not empty

        while len(questionsBatch) > 0:
            currQuestionIdx = 1
            lastSetId = ""
            lastResponseId = ""
            while currQuestionIdx < len(questionsBatch)+1:
                # get curr idx, compare to last set id to know whther to remove the response from possible answers
                currQuestion = getQuestionByIdx(questionsBatch, currQuestionIdx)

                currQuestionPossibleResponses = []
                for currResponse in currQuestion.possibleResponses:
                    if currQuestion.setId != lastSetId or (currQuestion.setId == lastSetId and currResponse.dependency != lastResponseId):
                        #this is a part of a set, we need to consider the last answer
                        currQuestionPossibleResponses.append(currResponse)

                if "Q999" not in currQuestion.id:
                    # this is a regular question (not tail)                        
                    selectedIndex = random.randint(0,len(currQuestionPossibleResponses)-1)

                    selectedResponse = currQuestionPossibleResponses[selectedIndex]
                    lastResponseId = selectedResponse.id

                    if currQuestion.setId != lastSetId:
                        #this is a new set
                        lastSetId = currQuestion.setId

                    gateway.set_journey_question_response(userId=userId, questionId=currQuestion.id, responseId=selectedResponse.id)
                    currUserResponseReport = reportResponseData()
                    currUserResponseReport.questionId = currQuestion.id
                    currUserResponseReport.id = selectedResponse.id
                    currUserResponseReport.idx = selectedResponse.idx
                    currUserResponseReport.motivationId = selectedResponse.motivationId

                    currUserJourneyReport.userResponses.append (currUserResponseReport)
                else:
                    responsesList = random.sample(currQuestion.possibleResponses, currQuestion.userResponsesNo)
                    
                    gateway.set_journey_multiple_question_responses(userId=userId, questionId=currQuestion.id, responses=responsesList)

                    for currResponseData in responsesList:
                        currUserResponseReport = reportResponseData()
                        currUserResponseReport.questionId = currQuestion.id
                        currUserResponseReport.id = currResponseData.id
                        currUserResponseReport.idx = currResponseData.idx
                        currUserResponseReport.motivationId = currResponseData.motivationId

                        currUserJourneyReport.userResponses.append (currUserResponseReport)

                currQuestionIdx +=1

            questionsBatch = gateway.get_next_questions_batch(userId, 1)
            
        currentUser = gateway.get_user(userId, "")
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