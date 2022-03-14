import json
from threading import current_thread
from pymongo import response
from pymongo.mongo_client import MongoClient
from discoveryData import UserDiscoveryJourneyData, JourneyResolutionData, UserDiscoveryJourneyState
from generalData import UserContextData, UserMotivationData, DiscoveryStatus
from discoveryData import DiscoveryBatchData
from moovLogic import MoovLogic
from questionsData import QuestionData, ResponseData, QuestionsType
import uuid
from loguru import logger

SINGLE_JOURNEY_ID = "J001"
TAIL_QUESTION_ID = "Q999"
MOTVIATION_TAIL_RESOLUTION_RESPONSE_SCORE = 1.3


def startUserJourney (userId, journeyTypeId = SINGLE_JOURNEY_ID):
    #creates an entry in discovery Journey if one doesn't exists, returns the user journey id
    
    dbInstance = MoovLogic()
    existingDiscoveryJourney = dbInstance.getUserDiscoveryJourney(userId)
    
    if (existingDiscoveryJourney is not None and existingDiscoveryJourney.state != "close"):
        #reset current journey
        existingDiscoveryJourney.currBatch = ""
        existingDiscoveryJourney.userResponses = {}

        dbInstance.insertOrUpdateDiscoveryJourney(existingDiscoveryJourney)
        dbInstance.setUserDiscoveryStatus(userId, discoveryStatus=DiscoveryStatus.ONGOING)
        return existingDiscoveryJourney.id


    newDiscoveryJourney = UserDiscoveryJourneyData()
    newDiscoveryJourney.id = userId + "_" + str(uuid.uuid4())[:8]
    newDiscoveryJourney.userId = userId
    #current we only have one journey
    newDiscoveryJourney.journeyId = journeyTypeId
    newDiscoveryJourney.state = UserDiscoveryJourneyState.NEW
    newDiscoveryJourney.currBatch = ""

    dbInstance.insertOrUpdateDiscoveryJourney(newDiscoveryJourney)
    dbInstance.setUserDiscoveryStatus(userId, discoveryStatus=DiscoveryStatus.ONGOING)

    return newDiscoveryJourney.id

def continueUserJourney (userId):
    dbInstance = MoovLogic()
    userJourneyId = dbInstance.getUserDiscoveryJourney(userId)

    if userJourneyId is None:
        userJourneyId = startUserJourney(userId=userId)

    return userJourneyId

def getCurrentQuestionsBatch (userId, userContext: UserContextData):
    dbInstance = MoovLogic()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

    if discoveryJourneyDetails is None:
        return None

    currBatchDetails = dbInstance.getDiscvoeryBatch(batchId = discoveryJourneyDetails.currBatch, userContext=userContext)

    # it might be that we still don't have a current batch as we just started
    if (currBatchDetails is not None):
        return currBatchDetails

    # as the curr batch is none - this will return the first batch
    nextBatchDetails = dbInstance.getDiscvoeryBatch(journeyId= discoveryJourneyDetails.journeyId, userContext=userContext)

    return nextBatchDetails

def getQuestionsInBatch (userId, userContext : UserContextData):
    # gets the current user batch from the journey collection and finds the current batch. 
    # gets the journey data and checks whether there are more batches. 
    # if there are - return the next questions batch and update the user journey data 
    # if this was the last batch - validate that we have a clear top 5 motivations - if not, create a tail resolution batch return DICOVERY_JOURNEY_END
    dbInstance = MoovLogic()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)   

    if discoveryJourneyDetails is None:
        return None

    currBatchDetails = dbInstance.getDiscvoeryBatch(batchId = discoveryJourneyDetails.currBatch, userContext=userContext)

    currBatchIdx = 0

    # it might be that we still don't have a current batch as we just started
    if (currBatchDetails is not None):
        currBatchIdx = currBatchDetails.batchIdx
        #check if the user have finished answering the questions in this batch (it might be that he have stopped and continued)
        # user Context is set to None - ad hoc questions have no localaziation option so bypass the getQuestion buildFromJson issues 
        if (currBatchDetails.batchId == 'B99' and 'Q99' not in  discoveryJourneyDetails.lastAnsweredQuestion):
            remainingQuestions = []

            #the user broke from the journey in the tail resolution part
            lastAnsweredQuestionDetails = dbInstance.getQuestion(discoveryJourneyDetails.lastAnsweredQuestion, userContext=userContext)
            
            remainingQuestions.append (lastAnsweredQuestionDetails)

            return remainingQuestions
        else:

            userRespondedLastBatchQuestion = False

            if (currBatchDetails.batchId == 'B99'):
                if (discoveryJourneyDetails.tailResolutionQuestionId == discoveryJourneyDetails.lastAnsweredQuestion):
                    userRespondedLastBatchQuestion = True
            else:
                questionsList = dbInstance.getQuestionsFromBatch(currBatchDetails.batchId, userContext=userContext)
                lastQuestionIdx = len(questionsList)
                lastQuestion = next((x for x in questionsList if x.batchIdx == lastQuestionIdx), None)
                if (lastQuestion is not None and lastQuestion.id == discoveryJourneyDetails.lastAnsweredQuestion):
                    userRespondedLastBatchQuestion = True
            
            if (not userRespondedLastBatchQuestion):         
                # the user have not finished to answer all the questions in the current batch, return the remaining questions
                remainingQuestions = []

                lastAnsweredQuestionDetails = dbInstance.getQuestion(discoveryJourneyDetails.lastAnsweredQuestion, userContext)

                for currQuestion in questionsList:
                    # it might be that this is the first answered question - so lastAnsweredQuestion will be None
                    if lastAnsweredQuestionDetails is None or currQuestion.batchIdx > lastAnsweredQuestionDetails.batchIdx:
                        # if the currQuestions Idx is bigger than the last questions' Idx  - add them to the remaning questions list
                        remainingQuestions.append (currQuestion)

                return remainingQuestions
    else:
        #curr batch details is none - this is the first time we get the batch request
        discoveryJourneyDetails.state = UserDiscoveryJourneyState.STANDARD_QUESTIONER
    
    nextBatchDetails = None
    
    if (discoveryJourneyDetails.state == UserDiscoveryJourneyState.STANDARD_QUESTIONER):
        # this is an on going regular questioner - get next questions batch
        nextBatchDetails = dbInstance.getDiscvoeryBatch(journeyId= discoveryJourneyDetails.journeyId, batchIdx=currBatchIdx + 1, userContext=userContext)

    questionsList = []

    if (nextBatchDetails is None):
        #no next batches exists verify that there is no tail - if there is, resolve it, if not - go to net phase
        motivationScoreBoard = summerizeUserResults(discoveryJourneyDetails, userContext=None)

        journeyResolutionDetails = getUserScoreBoardResolutionDetails(motivationScoreBoard)

        if journeyResolutionDetails.motivationsToResovleCount > 0:
            #the results are not valid - we need a tie breaker (resolve the tail)
            tailResQuestion = createTailResolutionQuestion(journeyResolutionDetails, userContext=userContext)

            questionsList.append(tailResQuestion) 

            discoveryJourneyDetails.state = UserDiscoveryJourneyState.TAIL_RESOLUTION
            discoveryJourneyDetails.currBatch = tailResQuestion.batchId
            discoveryJourneyDetails.tailResolutionQuestionId = tailResQuestion.id
            dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)

        elif discoveryJourneyDetails.state == UserDiscoveryJourneyState.STANDARD_QUESTIONER or discoveryJourneyDetails.state == UserDiscoveryJourneyState.TAIL_RESOLUTION:
            # user is done with the standard questioneer - create gap scoring questions
            questionsList = createGapScoringQuestions(journeyResolutionDetails, userContext)

            discoveryJourneyDetails.state = UserDiscoveryJourneyState.GAP_SCORING
            dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)

        else:
            # no tail and no more batches - check if we were in gap scoring phase - if so, end journey
            if (discoveryJourneyDetails.state == UserDiscoveryJourneyState.GAP_SCORING):
                sortedScoreBoard = dict(sorted(motivationScoreBoard.items(), key=lambda item: item[1], reverse= True))

                topFiveMotivations = {}
                motivationIdx = 0
                for key,value in sortedScoreBoard.items():

                    motivationGapScore = 0
                    if (key in discoveryJourneyDetails.motivationsGap):
                        motivationGapScore = discoveryJourneyDetails.motivationsGap[key]
                    
                    userMotviationDetails = UserMotivationData(motivationId=key, journeyScore=value, gapFactor=motivationGapScore)

                    topFiveMotivations[key] = userMotviationDetails
                    motivationIdx +=1

                    if motivationIdx > 4:
                        break
                
                endUserJourney(userId, topFiveMotivations)
    else:
        #discovery journey is on going - just get the next batch
        discoveryJourneyDetails.state = UserDiscoveryJourneyState.STANDARD_QUESTIONER
 
        discoveryJourneyDetails.currBatch = nextBatchDetails.batchId
        #updaing user discovery journey
        dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)
        
        #getting the list of questions in the next batch
        questionsList = dbInstance.getQuestionsFromBatch(nextBatchDetails.batchId, userContext=userContext)

    return questionsList

def setUserResponse (userId, questionId, responseId, userContext: UserContextData):
    dbInstance = MoovLogic()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

    if discoveryJourneyDetails is None:
        return None

    # qet question with no context
    currQuestionDetails = dbInstance.getQuestion(id=questionId, userContext=None)

    if (currQuestionDetails.batchId == 'B99'):
        # this is a tail resolution Question with a single response
        return setUserMultipleResponses (userId=userId, questionId=questionId, responses=[responseId])

    if (currQuestionDetails.type == QuestionsType.REGULAR):
        discoveryJourneyDetails.userResponses[questionId] = responseId
        discoveryJourneyDetails.lastAnsweredQuestion = questionId

    if (currQuestionDetails.type == QuestionsType.MOTIVATION_GAP):
        responseDetails = next((x for x in currQuestionDetails.possibleResponses if x.id == responseId), None)
        
        if (responseDetails is None):
            return

        discoveryJourneyDetails.motivationsGap[currQuestionDetails.motivationId] = convertResponseScoreToMotivationGapScore(score=responseDetails.motivationScore) 

    dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)

def convertResponseScoreToMotivationGapScore (score):
    return score

def setUserScoredResponse (userId, questionId, score, userContext: UserContextData):
    dbInstance = MoovLogic()
    discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

    if discoveryJourneyDetails is None:
        return None

    currQuestionDetails = dbInstance.getQuestion(id=questionId, userContext=userContext)

    if (currQuestionDetails.type == QuestionsType.MOTIVATION_GAP):
        discoveryJourneyDetails.motivationsGap[currQuestionDetails.motivationId] = convertResponseScoreToMotivationGapScore(score=score) 
        dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)

def setUserMultipleResponses (userId, questionId, responses):
    if (TAIL_QUESTION_ID in questionId):
        dbInstance = MoovLogic()
        discoveryJourneyDetails = dbInstance.getUserDiscoveryJourney(userId)

        if discoveryJourneyDetails is None:
            return None

        # add the responses for questions keys Q999_1, Q999_2 etc.
        for currResponseIndex, currResponse in enumerate(responses):
            currQuestionId = questionId + "_" + str(currResponseIndex)
            discoveryJourneyDetails.userResponses[currQuestionId] = currResponse.id
            
        discoveryJourneyDetails.lastAnsweredQuestion = questionId

        dbInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyDetails)    

def summerizeUserResults (userDiscoveryJourney, userContext : UserContextData):
    # get the disvcovery journey data for the user
    # create a dictionaray from all the different motivations ids as keys, and 0.0 score as value - userMotivationsScoreBoard
    # get the responses array and for eachquestion, find the response motivation score and update the userMotivationsScoreBoard
    # return the score board
    dbInstance = MoovLogic()
    motivationsIds = dbInstance.getAllMotivationsIds()

    # create a dict of {MotivationId, Score}
    motivationsScoreBoard = {}
    motivationsScoreBoard = dict.fromkeys(motivationsIds, 0)

    for currQuestionId in userDiscoveryJourney.userResponses:
        currResponseId = userDiscoveryJourney.userResponses[currQuestionId]

        actualCurrQuestionId = currQuestionId
        #check if this is a tail question 
        if TAIL_QUESTION_ID in currQuestionId:
             #we need to extract the question from the list remove the suffix _1 / _2 etc.
            actualCurrQuestionId = currQuestionId[:currQuestionId.rfind('_')]

        # no need for localized text
        currQuestion = dbInstance.getQuestion(id=actualCurrQuestionId, userContext=userContext)
        
        foundResponseData = None
        for currResponse in currQuestion.possibleResponses:
            if currResponse.id == currResponseId:
                foundResponseData = currResponse
                break

        if foundResponseData is not None:
            #add score to the score board
            motivationsScoreBoard[foundResponseData.motivationId] += foundResponseData.motivationScore

    return motivationsScoreBoard

def getUserScoreBoardResolutionDetails (userMotivationsScoreBoard):
    #returns true if there are clear top 5 motivations, false other wise
    sortedScoreBoard = dict(sorted(userMotivationsScoreBoard.items(), key=lambda item: item[1], reverse= True))
    scoreList = list(sortedScoreBoard.values())
    motivationsList = list(sortedScoreBoard)

    if (scoreList[4] > scoreList[5]):
        #no tail - return empty object
        motivationsTopList = motivationsList[:5].copy()
        return JourneyResolutionData(motivationsToResolveCount=0, motivationsList=motivationsTopList)

    motivationsTopList = []
    currScoreIndex = 0
    #start from 1 as we have at least one to resolve
    motivationsToResolveCount = 1
    motivationsTopList.append(motivationsList[4])
    #check score tail
    while currScoreIndex < len(sortedScoreBoard):
        if (scoreList[currScoreIndex] == scoreList[4] and currScoreIndex < 4):
            # before the top 5
            motivationsTopList.append(motivationsList[currScoreIndex])
            motivationsToResolveCount += 1
        elif (scoreList[currScoreIndex] == scoreList[4] and currScoreIndex > 4):
            # after the top 5
            motivationsTopList.append(motivationsList[currScoreIndex])
        elif (scoreList[4] > scoreList[currScoreIndex] and currScoreIndex > 4):
            # we are out of the tail
            break
      
        currScoreIndex += 1

    resolutionDetails = JourneyResolutionData(motivationsToResolveCount=motivationsToResolveCount, motivationsList=motivationsTopList)
    return resolutionDetails

def endUserJourney (userId, userMotivationScoreBoard):
    #end the journey and update the user data with the top 5 motivations
    dbInstance = MoovLogic()
    currJourney = dbInstance.getUserDiscoveryJourney(userId)

    currJourney.currBatch = ""
    currJourney.state = "closed"

    dbInstance.insertOrUpdateDiscoveryJourney(currJourney)
    dbInstance.setMotivationsToUSer(userId, userMotivationScoreBoard)
    dbInstance.setUserDiscoveryStatus(userId, discoveryStatus=DiscoveryStatus.DISCOVERED)

    # call Logic to perform post journey actions
    dbInstance.userJourneyEnded(userId)

def createTailResolutionQuestion (tailResolutionDataInstance, userContext: UserContextData):
    dbInstance = MoovLogic()
    tailResolutionQuestion = dbInstance.getQuestion(TAIL_QUESTION_ID, userContext)

    tailResolutionQuestion.id = TAIL_QUESTION_ID + "_" + str(uuid.uuid4())[:8]

    #now change the <<N>> to state the number of options the user needs to pick
    tailResolutionQuestion.questionText = tailResolutionQuestion.questionText.replace("<<N>>", str(tailResolutionDataInstance.motivationsToResovleCount))

    tailResolutionQuestion.userResponsesNo = tailResolutionDataInstance.motivationsToResovleCount

    for currResponseIdx, currMotviationId in enumerate(tailResolutionDataInstance.motivationsList):
        currMotivation = dbInstance.getMotivation(currMotviationId, userContext)

        currResponse = ResponseData()
        # setting the motivation id as response id, as we can't access this response when calculating score 
        currResponse.id = str(uuid.uuid4())[:8] 
        currResponse.idx = currResponseIdx
        currResponse.motivationId = currMotviationId
        currResponse.motivationScore = MOTVIATION_TAIL_RESOLUTION_RESPONSE_SCORE
        currResponse.questionId = tailResolutionQuestion.id
        currResponse.responseText = currMotivation.tailResolution

        tailResolutionQuestion.possibleResponses.append (currResponse)

    dbInstance.insertOrUpdateQuestion(tailResolutionQuestion)

    return tailResolutionQuestion

def createGapScoringQuestions (motivationsResolutionDetails : JourneyResolutionData, userContext: UserContextData):
    dbInstance = MoovLogic()
    return dbInstance.getMotivationGapQuestionsByMotivationsIds(motivationsResolutionDetails.motivationsList, userContext=userContext)