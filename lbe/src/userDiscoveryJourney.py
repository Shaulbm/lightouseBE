from threading import current_thread
from pymongo import response
from pymongo.mongo_client import MongoClient
from discoveryData import UserDiscoveryJourneyData, TailResolutionData
from mongoDB import moovDBInstance
from questionsData import QuestionData, ResponseData
import uuid

SINGLE_JOURNEY_ID = "J001"
TAIL_QUESTION_ID = "Q999"
MOTVIATION_TAIL_RESOLUTION_RESPONSE_SCORE = 1.3

def startUserJourney (userId, journeyTypeId = SINGLE_JOURNEY_ID):
    #creates an entry in discovery Journey if one doesn't exists, returns the user journey id
    
    dbInstance = moovDBInstance()
    existingDiscoveryJourney = dbInstance.getUserDiscoveryJourney(userId)
    
    if (existingDiscoveryJourney is not None and existingDiscoveryJourney.status != "close"):
        return existingDiscoveryJourney.id


    newDiscoveryJourney = UserDiscoveryJourneyData()
    newDiscoveryJourney.id = userId + "_" + str(uuid.uuid4())[:8]
    newDiscoveryJourney.userId = userId
    #current we only have one journey
    newDiscoveryJourney.journeyId = journeyTypeId
    newDiscoveryJourney.status = "new"

    dbInstance.insertOrUpdateDiscoveryJourney(newDiscoveryJourney)

    return newDiscoveryJourney.id

def getNextQuestionsBatch (userId, locale):
    # gets the current user batch from the journey collection and finds the current batch. 
    # gets the journey data and checks whether there are more batches. 
    # if there are - return the next questions batch and update the user journey data 
    # if this was the last batch - validate that we have a clear top 5 motivations - if not, create a tail resolution batch return DICOVERY_JOURNEY_END
    dbInstance = moovDBInstance()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

    if discoveryJourneyDetails is None:
        return None

    currBatchDetails = dbInstance.getDiscvoeryBatch(batchId = discoveryJourneyDetails.currBatch, locale=locale)

    currBatchIdx = 0

    # it might be that we still don't have a current batch as we just started
    if (currBatchDetails is not None):
        currBatchIdx = currBatchDetails.batchIdx

    nextBatchDetails = dbInstance.getDiscvoeryBatch(journeyId= discoveryJourneyDetails.journeyId, batchIdx=currBatchIdx + 1)

    questionsList = {}

    if (nextBatchDetails is None):
        #no next batches exists verify that there is no tail - if there is, resolve it, if not - do nothing, return an empty questions list
        motivationScoreBoard = summerizeUserResults(discoveryJourneyDetails)

        motivationsTail = getUserScoreBoardTail(motivationScoreBoard)

        if (len(motivationsTail.motivationsTail) > 0):
            #the results are not valid - we need atie breaker (resolve the tail)
            questionsList = createTailResolutionQuestion(motivationsTail, locale)
        else:
            # no tail and no more batches - process is done
            endUserJourney(userId, motivationScoreBoard)
    else:
        #discovery journey is on going - just get the next batch

        discoveryJourneyDetails.currBatch = nextBatchDetails.batchId
        #updaing user discovery journey
        dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)
        
        #getting the list of questions in the next batch
        questionsList = dbInstance.getQuestionsFromBatch(nextBatchDetails.batchId, locale)

    return questionsList

def setUserResponse (userId, questionId, responseId):
    dbInstance = moovDBInstance()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

    if discoveryJourneyDetails is None:
        return None

    discoveryJourneyDetails.userResponses[questionId] = responseId
    discoveryJourneyDetails.lastAnsweredQuestion = questionId

    dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)

def setUserMultipleResponses (userId, questionId, responsesIds):
    if (questionId == TAIL_QUESTION_ID):
        dbInstance = moovDBInstance()
        discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

        if discoveryJourneyDetails is None:
            return None

        # add the responses for questions keys Q999_1, Q999_2 etc.
        for currResponseIndex, currResponse in enumerate(responsesIds):
            currQuestionId = questionId + "_" + str(currResponseIndex)
            discoveryJourneyDetails.userResponses[currQuestionId] = currResponse
            
        discoveryJourneyDetails.lastAnsweredQuestion = questionId
        dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)    

def summerizeUserResults (userDiscoveryJourney, locale):
    # get the disvcovery journey data for the user
    # create a dictionaray from all the different motivations ids as keys, and 0.0 score as value - userMotivationsScoreBoard
    # get the responses array and for eachquestion, find the response motivation score and update the userMotivationsScoreBoard
    # return the score board

    motivationsIds = moovDBInstance.getAllMotivationsIds()

    # create a dict of {MotivationId, Score}
    motivationsScoreBoard = dict.fromkeys(motivationsIds, 0)

    for currQuestionId, currResponseId in userDiscoveryJourney.userResponses:

        actualCurrQuestionId = currQuestionId
        #check if this is a tail question 
        if TAIL_QUESTION_ID in currQuestionId:
             #we need to extract the question from the list remove the suffix _1 / _2 etc.
            actualCurrQuestionId = currQuestionId[:currQuestionId.rfind('_')]

        currQuestion = moovDBInstance.getQuestion(actualCurrQuestionId)
        
        foundResponseData = None
        for currResponse in currQuestion.possibleResponses:
            if currResponse.id == currResponseId:
                foundResponseData = currResponse
                break

        if foundResponseData is not None:
            #add score to the score board
            motivationsScoreBoard[currResponse.motivationId] += currResponse.motivationScore

    return motivationsScoreBoard

def getUserScoreBoardTail (userMotivationsScoreBoard):
    #returns true if there are clear top 5 motivations, false other wise
    sortedScoreBoard = dict(sorted(userMotivationsScoreBoard.items(), key=lambda item: item[1], reverse= True))
    scoreList = list(sortedScoreBoard.values())
    motivationsList = list(sortedScoreBoard)

    motivationsTail = []

    if (scoreList[4] > scoreList[5]):
        #no tail
        return motivationsTail

    currScoreIndex = 0
    #start from 1 as we have at least one to resolve
    motivationsToResolveCount = 1
    #check score tail
    while currScoreIndex < len(sortedScoreBoard):
        if (currScoreIndex < 5):
            if (scoreList[currScoreIndex] == scoreList[4] and currScoreIndex < 4):
                # before the top 5
                motivationsTail.append(motivationsList[currScoreIndex])
                motivationsToResolveCount += 1
            elif (scoreList[currScoreIndex == scoreList[4] and currScoreIndex > 4]):
                # after the top 5
                motivationsTail.append(motivationsList[currScoreIndex])
            elif (scoreList[4] > scoreList[currScoreIndex] and currScoreIndex > 4):
                # we are out of the tail
                break
      
        currScoreIndex += 1

    tailResult = TailResolutionData(motivationsToResolveCount=motivationsToResolveCount, motivationsList=motivationsTail)
    return tailResult

def endUserJourney (userId, userMotivationScoreBoard):
    #end the journey and update the user data with the top 5 motivations
    currJourney = moovDBInstance.getUserDiscoveryJourney(userId)

    currJourney.currBatch = ""
    currJourney.status = "closed"

    moovDBInstance.insertOrUpdateDiscoveryJourney(currJourney)
    moovDBInstance.setMotivationsToUSer(userMotivationScoreBoard)

def createTailResolutionQuestion (tailResolutionDataInstance, locale):
    tailResolutionQuestion = moovDBInstance.getQuestion(TAIL_QUESTION_ID, locale)

    tailResolutionQuestion.id = TAIL_QUESTION_ID + "_" + str(uuid.uuid4())[:8]

    #now change the <<N>> to state the number of options the user needs to pick
    tailResolutionQuestion.questionText.replace("<<N>>", str(tailResolutionDataInstance.motivationsToResovleCount))

    tailResolutionQuestion.userResponsesNo = tailResolutionDataInstance.motivationsToResovleCount

    for currResponseIdx, currMotviationId in enumerate(tailResolutionDataInstance.motivationsTail):
        currMotivation = moovDBInstance.getMotivation(currMotviationId)

        currResponse = ResponseData()
        # setting the motivation id as response id, as we can't access this response when calculating score 
        currResponse.id = str(uuid.uuid4())[:8] 
        currResponse.idx = currResponseIdx
        currResponse.motivationId = currMotviationId
        currResponse.motivationScore = MOTVIATION_TAIL_RESOLUTION_RESPONSE_SCORE
        currResponse.questionId = tailResolutionQuestion.Id
        currResponse.responseText = currMotivation.tailResolution

        tailResolutionQuestion.possibleResponses.append (currResponse)

    moovDBInstance.insertOrUpdateQuestion(tailResolutionQuestion)

    return tailResolutionQuestion
