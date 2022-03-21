from imp import release_lock
from itertools import count
from sqlite3 import Timestamp
import threading
from typing import Text
from fastapi import HTTPException
import string
import random
import uuid
from pymongo.common import RETRY_READS
from environmentProvider import EnvKeys
from issuesData import RelatedMotivationData
from issuesData import ConflictData
from motivationsData import InsightsUserType, InsightAggregationData
from moovData import IssueMoovData, ConflictMoovData, BaseMoovData, ExtendedIssueMoovData
from notificationsProvider import NotificationsProvider
from moovDB import MoovDBInstance
from generalData import UserData, UserPartialData, UserRoles, UserCircleData, Gender, Locale, UserContextData, UserCredData, UserRelationshipData, DiscoveryStatus
from singleton import Singleton
from loguru import logger
import datetime
import hashlib
from pathlib import Path
from cache import Cache
import environmentProvider as ep

ROOT_USER_IMAGES_PATH = 'C:\\Dev\\Data\\UserImages'
DEFAULT_USER_IMAGES_DIR = 'Default'

class MoovScheduler:
    def verifyTTLObjects():
        moovLogicInstance = MoovLogic()
        moovLogicInstance.verifyTTLForObjects()

class MoovLogic(metaclass=Singleton):
    def __init__(self):
        self.dataBaseInstance = MoovDBInstance()
        self.userContextLock = threading.Lock()
        self.usersContext = {}
        self.dbCache = Cache(self.dataBaseInstance)
        self.notificationsProvider = NotificationsProvider()

    def lock(self):
        self.counterLock.acquire()

    def release(self):
        self.counterLock.release()

    def setUserContextData(self, userId):

        # self.userContextLock.acquire()
        # try:
        #     if (userId in self.usersContext):
        #         userContextDetails = self.usersContext[userId]
        #         if ((datetime.datetime.utcnow() - userContextDetails.timeStamp) > datetime.timedelta(hours=12)):
        #             self.usersContext.pop(userId)
        #         else: 
        #             # print ("in setUserContextData - user context found and is ", userContextDetails.toJSON())
        #             return userContextDetails
            
        #     # userId is not found / found and removed since TTL was breached
        #     userDetails = self.getUser(userId)
        #     userContextDetails = UserContextData(userId=userId, firstName=userDetails.firstName, lastName=userDetails.familyName, locale=userDetails.locale)

        #     userContextDetails.timeStamp = datetime.datetime.utcnow()
        #     self.usersContext[userId] = userContextDetails
        # finally:
        #     self.userContextLock.release()

        # print ('in setUserContextData - new user Context created and is ', userContextDetails.toJSON())
        # return userContextDetails
        pass


    def getUserContextData(self, userId):
        
        # print ('in getUserContextData user id is ', userId)
        userContextDetails = None

        # self.userContextLock.acquire()
        # try:
        #     if (userId  in self.usersContext):
            
        #         userContextDetails = self.usersContext[userId]
        #     # print ('found user context and is ', userContextDetails.toJSON())
        # finally:
        #     self.userContextLock.release()

        # if (userContextDetails is None):
        #     userContextDetails = self.setUserContextData(userId)

        userDetails = self.getUser(userId)

        if userDetails:
            userContextDetails = UserContextData(userId=userId, firstName=userDetails.firstName, lastName=userDetails.familyName, gender=userDetails.gender, locale=userDetails.locale, isRTL=userDetails.isRTL)

        return userContextDetails

    def verifyTTLForObjects(self):
        self.verifyTTLForActiveMoovs()

    def verifyTTLForActiveMoovs(self):
        # get all active moovs - filter by end time < now.
        # mark as overdue for theseactive moovs
        # send mail to each of these moovs
        
        print ('in MoovLogic.verifyTTL time is ', str(datetime.datetime.utcnow()))
        foundMoovs = self.getAllMoovsPlannedToEnd(datetime.datetime.utcnow())

        for currMoov in foundMoovs:
            # just mark as overdue
            currMoov.isOverdue = True
            self.dataBaseInstance.updateMoovInstane(currMoov)
            
        # find those moovs that are ending and send notifcations
        timeToNotifyBeforeOverdue = ep.getAttribute(EnvKeys.behaviour, EnvKeys.hoursToNotifyBeforMoovsOverdue) 
        foundMoovs = self.getAllMoovsPlannedToEnd(datetime.datetime.utcnow() + datetime.timedelta(hours=timeToNotifyBeforeOverdue))

        for currMoov in foundMoovs:
            userContext = self.getUserContextData(currMoov.userId)
            counterpartDetails = self.getUser(currMoov.counterpartId)
            currMoovData = self.getBaseMoov(id=currMoov.moovId, counterpartDetails= counterpartDetails , userContext=userContext)

            userDetails = self.getUser(currMoov.userId)
                             
            if (len(currMoov.counterpartsIds) == 1):
                counterpartDetails = self.getUser(currMoov.counterpartsIds[0])
                self.notificationsProvider.sendIssueMoovIsAboutToOverdue(moovOwner=userDetails,moovCounterpart=counterpartDetails, moovName=currMoovData.name)
            else:
                self.notificationsProvider.sendConflictMoovIsAboutToOverdue(moovOwner=userDetails, moovName=currMoovData.name)
            
            # marking that we notified the user, it will not be called again
            currMoov.notifiedUserForOverdue = True
            self.dataBaseInstance.updateMoovInstane(currMoov)         

    def getDatabase(self):
        return self.dataBaseInstance

    def getNextCount(self):
        return self.dataBaseInstance.getNextCount()

    def getTextDataByParent (self, parentId, locale, gender, name = ""):
        localedText = self.dataBaseInstance.getTextDataByParent(parentId=parentId, locale=locale, gender=gender, name=name)

        return localedText

    def getTextDataByParents (self, parentsIds, locale, gender, name = ""):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale, gender, name=name)

        return resultTextDict

    def insertOrUpdateMotivation (self, motivationDetails):
        self.dataBaseInstance.insertOrUpdateMotivation (motivationDetails)

    def insertOrUpdateMotivationInsight (self, insightDetails):
        self.dataBaseInstance.insertOrUpdateMotivationInsight (insightDetails)

    def insertOrUpdateInsightType (self, insightTypeDetails):
        self.dataBaseInstance.insertOrUpdateInsightType(insightTypeDetails)

    def getInsightsForCounterpart(self, counterpartId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)

        insights = self.dataBaseInstance.getInsightsForCounterpart (counterpartDetails, userContext)

        insightsTypes = self.dataBaseInstance.getInsightsTypes (InsightsUserType.TEAM_MEMBER , userContext, counterpartDetails=counterpartDetails)

        aggregatedInsights = []

        for currInsight in insightsTypes:
            currAggInsihgt = InsightAggregationData()

            filterdInsights = [x for x in insights if x.insightId == currInsight.id]

            currAggInsihgt.insightType = currInsight
            currAggInsihgt.insights = filterdInsights.copy()

            aggregatedInsights.append(currAggInsihgt)

        return aggregatedInsights

    def getInsightsForSelf(self, userContext: UserContextData):
        userDetails = self.getUser(userContext.userId)
        insights = self.dataBaseInstance.getInsightsForSelf (userDetails, userContext)

        insightsTypes = self.dataBaseInstance.getInsightsTypes (InsightsUserType.SELF , userContext)

        aggregatedInsights = []

        for currInsight in insightsTypes:
            currAggInsihgt = InsightAggregationData()

            filterdInsights = [x for x in insights if x.insightId == currInsight.id]

            currAggInsihgt.insightType = currInsight
            currAggInsihgt.insights = filterdInsights.copy()

            aggregatedInsights.append(currAggInsihgt)

        return aggregatedInsights


    def insertOrUpdateMoov (self, moovDataObj):
        self.dataBaseInstance.insertOrUpdateMoov(moovDataObj)

    def insertOrUpdateConflictMoov (self, moovDataObj):
        self.dataBaseInstance.insertOrUpdateConflictMoov(moovDataObj)

    def getConflictMoovs (self, conflictId, userContext: UserContextData):
        moovs = self.dataBaseInstance.getConflictMoovs (conflictId=conflictId, userContext=userContext)

        for currMoov in moovs:
            # moovConflictDetails = self.getConflict(conflictId, userContext=None)
            # currently the conflict moov score is already set to the conflict score in MoovDB. good enough for this stage.
            moovConflictDetails = None
            currMoov.score = self.calculateConflictMoovScore(currMoov, moovConflictDetails)

    def getConflictsMoovsForUsers (self, teamMemberId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getConflictsMoovsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, userContext=userContext)

    def getIssueMoov (self, id, userContext: UserContextData):
        return self.getDatabase().getIssueMoov(id=id, userContext=userContext)

    def getBaseMoov (self, id, counterpartDetails, userContext: UserContextData):
        return self.dataBaseInstance.getBaseMoov(id=id, counterpartDetails=counterpartDetails, userContext=userContext)

    def getMoovsForIssueAndCounterpart (self, counterpartId, issueId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        issueMoovs :list (IssueMoovData) = self.dataBaseInstance.getMoovsForIssueAndCounterpart(counterpartDetails=counterpartDetails, issueId=issueId, userContext=userContext)

        issueDetails = self.getIssue(issueId, userContext = None)

        extendedIssueMoovs = []

        pastMoovs = self.getPastMoovsToCounterpart(userId = userContext.userId, counterpartId = counterpartId, userContext = userContext)
        activeMoovs = self.getActiveMoovsToCounterpart(userId=userContext.userId, counterpartId=counterpartId, userContext=userContext)

        for currMoov in issueMoovs:
            relatedMotivation = next((x for x in issueDetails.contributingMotivations if x.motivationId == currMoov.motivationId), None)
            
            if relatedMotivation is not None:
                currMoov.score = self.calculateIssueMoovScore(counterpartId=counterpartId, moov=currMoov, relatedMotivation=relatedMotivation, pastMoovs= pastMoovs, activeMoovs=activeMoovs)

            # create steps for moov
            extendedMoov = ExtendedIssueMoovData()
            extendedMoov.fromIssueMoov(currMoov)
            extendedMoov.steps = self.getStepsToMoov (currMoov)
            extendedIssueMoovs.append(extendedMoov)

        return extendedIssueMoovs

    def doesMoovHaveRelevantInstances(self, pastMoovs, activeMoovs, moovId):
        relevantPastMoovs = [moov for moov in pastMoovs if moov.moovId == moovId]

        for activeMoov in activeMoovs:
            # if the is an active moov with this id return true
            if activeMoov.moovId == moovId:
                return True

        for pastMoov in relevantPastMoovs:
            # if there is a past moov in the defined timeframe, return true
            timeFromMoovEnd = datetime.datetime.utcnow() - pastMoov.endDate
            if timeFromMoovEnd.days < ep.getAttribute(EnvKeys.moovs, EnvKeys.pastMoovScorePenaltyDays):
                return True

        return False

    def getStepsToMoov (self, moovData : BaseMoovData):
        moovSteps = moovData.howTo.split('*')

        if (moovSteps[0] == ''):
            # it might be that the first char is '*' - this creates an empty step
            del(moovSteps[0])

        return moovSteps


    def calculateIssueMoovScore (self, counterpartId, moov : IssueMoovData, relatedMotivation : RelatedMotivationData, pastMoovs, activeMoovs):
        userMotivationGap = self.getUserMotivationGap(userId=counterpartId, motivationId=relatedMotivation.motivationId) / ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase)

        multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        
        calculatedScore = 0
        calculatedScore += moov.score
        calculatedScore += relatedMotivation.impact 
        calculatedScore += multiplyer*userMotivationGap
        calculatedScore = moov.score + relatedMotivation.impact + multiplyer*userMotivationGap
        
        # normalize - get the % of 100
        normalizedScore = calculatedScore / (multiplyer*3) * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)

        if self.doesMoovHaveRelevantInstances(pastMoovs=pastMoovs, activeMoovs=activeMoovs, moovId=moov.id):
            # if the moov was done in the last X days then the score should be penallize
            normalizedScore = normalizedScore * ep.getAttribute(EnvKeys.moovs, EnvKeys.moovInstanceScorePenaltyValue)

        return normalizedScore

    def calculateConflictMoovScore(self, moov : ConflictMoovData, conflictDetails : ConflictData):
        # return conflictDetails.score
        return moov.score

    def insertOrUpdateText (self, dataCollection, textDataObj):
        self.dataBaseInstance.insertOrUpdateText(dataCollection=dataCollection, textDataObj=textDataObj)
    
    def insertOrUpdateUserDetails (self, id, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, color = 0, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, color=color, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData : UserData):
        self.dataBaseInstance.insertOrUpdateUser(currUserData=currUserData)

        # update cache that user was changed
        self.dbCache.setUserDirty(currUserData.id)

    def createUser (self, notifyNewUser = False, setDefaultPassword = False, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        # get user details prior to potentially adding it to the DB
        existingUser = self.getUserByMail(mail=mailAddress)
        if (existingUser is not None):
            return existingUser.Id

        userId = str(uuid.uuid4())
        newUser = UserData(id=userId, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        newUser.color = self.generateUserColor()
        newUser.discoveryStatus = DiscoveryStatus.UNDISCOVERED

        self.dataBaseInstance.insertOrUpdateUser(currUserData=newUser)

        userPassword = ""
        if (setDefaultPassword):
            userPassword = ep.getAttribute(EnvKeys.defaults, EnvKeys.initialUserPassword)
        else:
            userPassword = self.createRandomPassword()

        self.setUserPassword(userId=userId, orgId=newUser.orgId, passwordRaw = userPassword)

        if (notifyNewUser):
            self.notificationsProvider.sendWelcomeMail(userName=newUser.firstName, userMail=newUser.mailAddress, password=userPassword)

        return newUser.id

    def resetUserPassword(self, userMail):
       # get user details prior to potentially adding it to the DB
        existingUser = self.getUserByMail(userMail)

        if existingUser is None:
            return

        userPassword = self.createRandomPassword()
        self.setUserPassword(userId=existingUser.id, orgId=existingUser.orgId, passwordRaw = userPassword)
        self.notificationsProvider.sendResetPassword(userName=existingUser.firstName, userMail=existingUser.mailAddress, newPassword=userPassword)

        # update cache that user was changed
        self.dbCache.setUserDirty(existingUser.id)        

    def createRandomPassword(self):
        # printing letters
        letters = string.ascii_letters
        

        # printing digits
        letters += string.digits

        #remove space from possible letters
        letters = letters.replace(" ","")
        newPassword = ( ''.join(random.choice(letters) for i in range(10)) )

        return newPassword

    def setUserDiscoveryStatus(self, userId, discoveryStatus):
        userDetails = self.getUser(userId)

        if (userDetails is not None):
            userDetails.discoveryStatus = discoveryStatus
            self.insertOrUpdateUser(userDetails)

    def generateUserColor(self):
        return ep.generateRandomUserColor()

    def setMotivationsToUSer (self, id, motivations):
        self.dataBaseInstance.setMotivationsToUSer(id=id, motivations=motivations)
        # update cache that user was changed
        self.dbCache.setUserDirty(id)

    def getMotivation (self, id, userContext: UserContextData):
        motivationDetails = self.dbCache.getMotivationDetailsById(motivationId=id, userContext=userContext)
        return motivationDetails
    
    def getAllMotivations(self,userContext:UserContextData):
        return self.dataBaseInstance.getAllMotivations(userContext=userContext)

    def getUserMotivations (self, userId, userContext:UserContextData):
        requestedUser = self.getUser(userId)

        if (requestedUser.motivations is None or requestedUser.motivations.__len__ == 0):
            return []

        motivationsIds = list(requestedUser.motivations.keys())

        foundMotivations = []

        for currMotivationId in motivationsIds:
            currMotivation = self.getMotivation(id=currMotivationId, userContext=userContext) 
            foundMotivations.append(currMotivation)

        return foundMotivations 

    def getAllMotivationsIds(self):
        return self.dataBaseInstance.getAllMotivationsIds()

    def userLogin(self, userMail, password):
        # print ('in userLogin received mail ', userMail, password)

        userMail = userMail.lower()

        userDetails : UserData = self.getUserByMail(mail=userMail)

        # TBD verify password

        partialUserDetails = None

        if (userDetails is not None):
            hashedPassword = hashlib.sha256(password.encode('utf-8'))

            if self.getUserPassword(userDetails.id) == hashedPassword.hexdigest():
                partialUserDetails = UserPartialData()
                partialUserDetails.fromFullDetails(userDetails)
            else:
                # raise error 404
                pass

        return partialUserDetails

    def getUserPassword (self, userId):
        return self.dataBaseInstance.getUserPassword(userId=userId)

    def setUserPassword (self, userId,orgId, passwordRaw):
        hashedPassword = hashlib.sha256(passwordRaw.encode('utf-8'))
        userCredDetails = UserCredData(id=userId, orgId=orgId, password=hashedPassword.hexdigest())

        self.dataBaseInstance.setUserPassword(userCredDetails)

    def getUserByMail (self, mail):
        return self.dataBaseInstance.getUserByMail(mail=mail)
    
    def getUser (self, id = ""):      
        userDetails = self.dbCache.getUSerDetailsById (id)

        return userDetails

    def insertOrUpdateQuestion(self, currQuestionData):
        self.dataBaseInstance.insertOrUpdateQuestion(currQuestionData=currQuestionData)

    def getQuestion(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getQuestion(id=id, userContext=userContext)

    def getQuestionsFromBatch(self, batchId, userContext:UserContextData):
        return self.dataBaseInstance.getQuestionsFromBatch(batchId=batchId, userContext=userContext)

    def getMotivationGapQuestionsByMotivationsIds (self, motivationsIdsList, userContext : UserContextData):
        return self.dataBaseInstance.getMotivationGapQuestionsByMotivationsIds(motivationsIdsList, userContext=userContext)

    def getUserDiscoveryJourney(self, userId):
        return self.dataBaseInstance.getUserDiscoveryJourney(userId=userId)

    def insertOrUpdateDiscoveryJourney(self, discoveryJourneyData):
        self.dataBaseInstance.insertOrUpdateDiscoveryJourney(discoveryJourneyData=discoveryJourneyData)

    def getDiscvoeryBatch(self, userContext: UserContextData, batchId = "", journeyId = "", batchIdx = ""):
        return self.dataBaseInstance.getDiscvoeryBatch(userContext=userContext, batchId=batchId, journeyId=journeyId, batchIdx=batchIdx)

    def insertOrUpdateIssue(self, currIssueData):
        self.dataBaseInstance.insertOrUpdateIssue(currIssueData=currIssueData)

    def getIssue(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getIssue(id= id, userContext=userContext)

    def insertOrUpdateConflict(self, currConflictData):
        self.dataBaseInstance.insertOrUpdateConflict(currConflictData=currConflictData)

    def getConflict(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getConflict(id, userContext=userContext)

    def getConflictsForUsers (self, teamMemberId, counterpartId, partialData: bool, userContext : UserContextData):
        return self.dataBaseInstance.getConflictsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, partialData=partialData, userContext=userContext)

    def getIssuesForSubject (self, subjectId, userContext: UserContextData):
        return self.dataBaseInstance.getIssuesForSubject(subjectId=subjectId, userContext=userContext)
    
    def getAllIssues (self, userContext: UserContextData):
        return self.dataBaseInstance.getAllIssues(userContext=userContext)
    
    def getIssueForCounterpart(self, issueId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getIssueForCounterpart(issueId=issueId, counterpartId=counterpartId, userContext=userContext)

    def insertOrUpdateSubject(self, currSubjectData):
        self.dataBaseInstance.insertOrUpdateSubject(currSubjectData=currSubjectData)

    def getAllSubjects(self, userContext: UserContextData):
        return self.dataBaseInstance.getAllSubjects(userContext=userContext)

    def getUserCircle(self, userId):
        userCircleDetails = UserCircleData()
        userCircleDetails.teamMembersList = self.getUsersUnder(userId)
        userCircleDetails.peopleOfInterest = self.getUserPeopleOfInterest(userId)

        return userCircleDetails

    def getUsersUnder (self, userId):
        return self.dataBaseInstance.getUsersUnder(userId=userId)

    def getUserPeopleOfInterest(self, userId):
        peopleOfInterestList = []

        requestingUser: UserData = self.getUser(id=userId)
        poiIdList = requestingUser.personsOfInterest 

        for currPOI in poiIdList:
            userPartialDetails = UserPartialData()
            userPartialDetails.fromFullDetails(self.getUser(id=currPOI))
            userPartialDetails.activeMoovsCount = self.dataBaseInstance.getActiveMoovsCountToCounterpart(userId=userId, counterpartId=userPartialDetails.id)
            userPartialDetails.recommendedMoovsCount = self.dataBaseInstance.getRecommnededMoovsAboveThresholdCount(userId=userId, counterpartId=userPartialDetails.id)
            peopleOfInterestList.append (userPartialDetails)

        return peopleOfInterestList

    def getUserImageFromFile(self, userId):
        userDetails = self.getUser(id=userId)

        if userDetails is None:
            return None

        file_used = ROOT_USER_IMAGES_PATH + '\\' + userDetails.orgId + '\\' + userDetails.id + '_small.jpg'

        # if the user image does not exists, user detauls images
        my_file = Path(file_used)
        if not my_file.exists():
            if userDetails.gender == Gender.MALE:
                file_used = ROOT_USER_IMAGES_PATH + '\\' + DEFAULT_USER_IMAGES_DIR + '\\' + 'male.png'
            else:
                file_used = ROOT_USER_IMAGES_PATH + '\\' + DEFAULT_USER_IMAGES_DIR + '\\'+ 'female.png'

        return file_used

    def activateIssueMoov (self, moovId, userId, counterpartId, userContext: UserContextData):
        moovDetails = self.getIssueMoov(moovId, userContext= None)

        moovInstancePriority = self.calculateIssueMoovPriority(userId = userId, counterpartId = counterpartId, motivationId=moovDetails.motivationId)
        return self.dataBaseInstance.activateIssueMoov(moovId=moovId, userId=userId, counterpartId=counterpartId, priority=moovInstancePriority, userContext=userContext)

    def activateConflictMoov (self, moovId, userId, counterpartsIds, userContext: UserContextData):
        # moovInstancePriority = self.calculateConflictMoovPriority(userId, counterpartsIds)
        # return self.dataBaseInstance.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, priority=moovInstancePriority, userContext=userContext)
        pass

    def extendAcctiveMoov(self, activeMoovId):
        activeMoovDetails = self.getActiveMoov(activeMoovId=activeMoovId)

        if (activeMoovDetails is not None):
            activeMoovDetails.plannedEndDate = datetime.datetime.utcnow() + datetime.timedelta(days=ep.getAttribute(EnvKeys.moovs, EnvKeys.extendActiveMoovTimeDays))
            activeMoovDetails.isOverdue = False
            self.insertOrUpdateActiveMoov(activeMoovDetails=activeMoovDetails)

        return activeMoovDetails

    def getActiveMoov (self, activeMoovId):
        return self.dataBaseInstance.getActiveMoov(id=activeMoovId)

    def insertOrUpdateActiveMoov(self, activeMoovDetails):
        self.dataBaseInstance.insertOrUpdateActiveMoov(activeMoov=activeMoovDetails)

    def calculateIssueMoovPriority(self, userId, counterpartId, motivationId):
        # multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        userRelationshipDetails : UserRelationshipData = self.getRelationshipData(userId=userId, counterpartId=counterpartId)

        seperationChancePart = 0
        seperationCostPart = 0
        motivationGapPart = 0

        if userRelationshipDetails is None:
            # set to 50% 
            seperationChancePart = 0.5
            seperationCostPart = 0.5
        else:
            seperationQuestionsScale = ep.getAttribute(EnvKeys.behaviour,EnvKeys.seperationQuestionsScale)
            seperationChancePart = userRelationshipDetails.seperationChanceEstimation/seperationQuestionsScale
            seperationCostPart = userRelationshipDetails.costOfSeperation/seperationQuestionsScale

        motivationGapPart = self.getUserMotivationGap(userId=counterpartId, motivationId=motivationId)/ ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase)
        calculatedPriority = seperationChancePart + seperationCostPart + motivationGapPart
        
        # normalize - get the % of 100
        normalizedPriorityValue = calculatedPriority / 3 * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)
        return normalizedPriorityValue

    def getUserMotivationGap (self, userId, motivationId):
        userDetails = self.getUser(userId)

        gapFactor = 0
        # motivationData = next((x for x in userDetails.motivations if x.motivationId == motivationId), None)
        if (motivationId in userDetails.motivations):
            gapFactor = userDetails.motivations[motivationId].gapFactor

        return gapFactor

    def calculateConflictMoovPriority(self, userId, counterpartsIds):
        if (len(counterpartsIds) != 2):
            # return avergage priority
            return ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority) / 2

        multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        seperationQuestionsScale = ep.getAttribute(EnvKeys.behaviour,EnvKeys.seperationQuestionsScale)


        firstUserRelationshipDetails : UserRelationshipData = self.getRelationshipData(userId=userId, counterpartId=counterpartsIds[0])
        secondUserRelationshipDetails : UserRelationshipData = self.getRelationshipData(userId=userId, counterpartId=counterpartsIds[1])

        if (firstUserRelationshipDetails is None or secondUserRelationshipDetails is None):
            # missing relationship details - return avergage priority
            return ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority) / 2

        firstCPCalculatedPriority = multiplyer*firstUserRelationshipDetails.seperationChanceEstimation/seperationQuestionsScale + multiplyer*firstUserRelationshipDetails.costOfSeperation/seperationQuestionsScale
        secondCPCalculatedPriority = multiplyer*secondUserRelationshipDetails.seperationChanceEstimation/seperationQuestionsScale + multiplyer*secondUserRelationshipDetails.costOfSeperation/seperationQuestionsScale

        # normalize - get the % of 100
        normalizedPriorityValue = (firstCPCalculatedPriority / (multiplyer*2) + secondCPCalculatedPriority / (multiplyer*2))/2 * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)
        return normalizedPriorityValue

    def getActiveMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        counterpartDetails = self.getUser(id=counterpartId)
        activeMoovs = self.dataBaseInstance.getActiveMoovsToCounterpart(userId=userId, counterpartDetails=counterpartDetails, userContext=userContext)

        #  calculate steps to moov 
        for activeMoov in activeMoovs:
            extendedMoovDetails = ExtendedIssueMoovData() 
            extendedMoovDetails.fromBase(activeMoov.moovData)
            extendedMoovDetails.description = self.setNameInText(text=extendedMoovDetails.description, name=counterpartDetails.firstName)
            extendedMoovDetails.howTo = self.setNameInText(text=extendedMoovDetails.howTo, name=counterpartDetails.firstName)
            extendedMoovDetails.reasoning = self.setNameInText(text=extendedMoovDetails.reasoning, name=counterpartDetails.firstName)
            extendedMoovDetails.steps = self.getStepsToMoov(extendedMoovDetails)
            activeMoov.moovData = extendedMoovDetails
            activeMoov.counterpartFirstName = counterpartDetails.firstName
            activeMoov.counterpartLastName = counterpartDetails.familyName
            activeMoov.counterpartColor = counterpartDetails.color
            activeMoov.isImportant = (activeMoov.priority >= ep.getAttribute(EnvKeys.moovs, EnvKeys.importanctPriorityThershold))

        return activeMoovs

    def getPastMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        return self.dataBaseInstance.getPastMoovsToCounterpart(userId=userId, counterpartDetails=counterpartDetails, userContext=userContext)

    def getPastMoovsToMoovAndCounterpart(self, userId, counterpartId, moovId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        return self.dataBaseInstance.getPastMoovsToMoovAndCounterpart(userId=userId, counterpartDetails=counterpartDetails, moovId=moovId, userContext=userContext)

    def getActiveMoovsForUser (self, userId, userContext: UserContextData):
        activeMoovs = self.dataBaseInstance.getPartialActiveMoovsForUser(userId=userId, userContext=userContext)

        #  calculate steps to moov
        for activeMoov in activeMoovs:
            counterpartDetails = self.getUser(activeMoov.counterpartId)
            moovDetails = self.getBaseMoov(id=activeMoov.moovId, counterpartDetails=counterpartDetails, userContext=userContext)
            extendedMoovDetails = ExtendedIssueMoovData() 
            extendedMoovDetails.fromBase(moovDetails)
            extendedMoovDetails.steps = self.getStepsToMoov(extendedMoovDetails)
            activeMoov.moovData = extendedMoovDetails
            # extendedMoovDetails.name = self.setNameInText(text=extendedMoovDetails.name, name=counterpartDetails.firstName)
            # extendedMoovDetails.description = self.setNameInText(text=extendedMoovDetails.description, name=counterpartDetails.firstName)
            # extendedMoovDetails.howTo = self.setNameInText(text=extendedMoovDetails.howTo, name=counterpartDetails.firstName)
            # extendedMoovDetails.reasoning = self.setNameInText(text=extendedMoovDetails.reasoning, name=counterpartDetails.firstName)            
            activeMoov.counterpartFirstName = counterpartDetails.firstName
            activeMoov.counterpartLastName = counterpartDetails.familyName
            activeMoov.counterpartColor = counterpartDetails.color
            activeMoov.isImportant = (activeMoov.priority >= ep.getAttribute(EnvKeys.moovs, EnvKeys.importanctPriorityThershold))

        return activeMoovs    

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId):
        activeMoov = self.dataBaseInstance.getActiveMoovByMoovUserAndCounterpart (userId=userId, moovId=moovId, counterpartId=counterpartId)

        #  calculate steps to moov
        extendedMoovDetails = ExtendedIssueMoovData() 
        extendedMoovDetails.fromBase(activeMoov.moovData)
        extendedMoovDetails.steps = self.getStepsToMoov(activeMoov.moovData)
        activeMoov.moovData = extendedMoovDetails 

        return activeMoov

    def endMoov (self, activeMoovId, feedbackScore, feedbackText, isEndedByTimer):
        self.dataBaseInstance.endMoov(activeMoovId=activeMoovId, feedbackScore=feedbackScore, feedbackText=feedbackText, isEndedByTimer=isEndedByTimer)
    
    def getAllMoovsPlannedToEnd (self, timeStamp, ignoreUserNotifications = False):
        return self.dataBaseInstance.getAllMoovsPlannedToEnd(timeStamp=timeStamp, ignoreUserNotifications = ignoreUserNotifications)

    def userJourneyEnded (self, userId):
        # gather all the relevant users to notify
        #   1. Direct Manager
        #   2. All those which these users are POI on
        # 
        # send notifications to all
        usersToNotify = []
        currUser = self.getUser(userId)
        currUserDirectManager = self.getUser(currUser.parentId)
        currUserPassivePOI = self.getInterestedusers(currUser.id)

        if len(currUserPassivePOI) > 0:
            usersToNotify += currUserPassivePOI
        
        if currUserDirectManager is not None: 
            usersToNotify.append(currUserDirectManager)        

        # notify to all who are interested in this user
        for userToNotify in usersToNotify:
            print ('user journey ended = notifying to {} users', usersToNotify.__len__())
            self.notificationsProvider.sendDiscoveryDoneMail(notifyTo=userToNotify.mailAddress, userWhoEndedDiscoveryDetails=currUser)    
    
    def getInterestedusers(self, userId):
        return self.dataBaseInstance.getInterestedUsers(userId)

    def insertOrUpdateRelationshipDetails (self, userId, counterpartId, costOfSeperation, chanceOfSeperation):
        relationshipDetails = UserRelationshipData(userId=userId, counterpartId=counterpartId, costOfSeperation=costOfSeperation, chanceOfSeperation=chanceOfSeperation, timeStamp=datetime.datetime.utcnow())

        self.insertOrUpdateRelationship(relationshipDetails)

    def insertOrUpdateRelationship (self, relationshipData):
        self.dataBaseInstance.insertOrUpdateRelationship(relationshipData= relationshipData)

    def getRelationshipData (self, userId, counterpartId):
        return self.dataBaseInstance.getRelationshipData (userId=userId, counterpartId=counterpartId)

    def missingRelationshipData (self, userId, counterpartId):
        existingRelationShipData = self.getRelationshipData(userId=userId, counterpartId=counterpartId)

        missingRelationshipDataRetVal = True

        if (existingRelationShipData is not None):

            exitingTime = datetime.datetime.strptime(existingRelationShipData.timeStamp, '%Y-%m-%dT%H:%M:%S.%f')
            relationshipTimeSpan = datetime.datetime.utcnow() - exitingTime

            if (relationshipTimeSpan.days < ep.getAttribute(EnvKeys.behaviour, EnvKeys.relationshipDataTTLDays)):
                missingRelationshipDataRetVal = False

        return missingRelationshipDataRetVal

    def getTopRecommendedMoovsForCounterpart(self, userId, counterpartId, userContext : UserContextData):
        allRecommendedMoovs = self.getALlRecommendedMoovsForCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

        sortedRecommendedMoovs = sorted(allRecommendedMoovs, key=lambda x: x.score, reverse=True)

        topRecommendedMoovsToReturn = ep.getAttribute(EnvKeys.moovs, EnvKeys.topRecommendedMoovsNo)
        recommendedMoovsThreshold = ep.getAttribute(EnvKeys.moovs, EnvKeys.topRecommendedMoovThreshold)

        topRecommendedMoovs = sortedRecommendedMoovs[:topRecommendedMoovsToReturn]

        topRecommendedMoovs = [rm for rm in topRecommendedMoovs if rm.score > recommendedMoovsThreshold]

        return topRecommendedMoovs 
        
    def getALlRecommendedMoovsForCounterpart(self, userId, counterpartId, userContext: UserContextData):
        recommendedMoovs = self.getMoovsForIssueAndCounterpart(counterpartId=counterpartId, issueId=ep.getAttribute(EnvKeys.moovs, EnvKeys.recommendedMoovsIssueId), userContext=userContext)

        return recommendedMoovs

    def setNameInText (self, text, name):
        tempText = text.replace("<<NAME>>", name)
        tempText = tempText.replace("<<>>", name)
        tempText = tempText.replace("<< >>", name)

        return tempText

    def updateUserDetails(self, id, locale, gender):
        userDetails = self.getUser(id)

        if (userDetails is None):
            raise HTTPException(status_code=404, detail="user not found")

        userDetails.locale = locale
        userDetails.gender = gender

        self.insertOrUpdateUser(userDetails)

        return userDetails

    def updateUserPassword(self, id, oldPassword, newPassword):
        userDetails = self.getUser(id)

        if (userDetails is None):
            raise HTTPException(status_code=404, detail="user not found")

        if (userDetails is not None):
            hashedPassword = hashlib.sha256(oldPassword.encode('utf-8'))
            self.setUserPassword(userId=id, orgId=userDetails.orgId, passwordRaw=newPassword)
            return ""
        else:
            raise HTTPException(status_code=401, detail="wrong password")

    def sendUserFeedback(self, userId, issue, text):
        userDetails = self.getUser(userId)
        return self.notificationsProvider.sendUserFeedback(userId=userId, userMail=userDetails.mailAddress, issue=issue, text=text)

    def sendDiscoveryReminder(self, counterpartId, userContext : UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        return self.notificationsProvider.sendDiscoveryReminder(notifyToMail=counterpartDetails.mailAddress, notifyToName=counterpartDetails.firstName, teamManagerName=userContext.firstName)