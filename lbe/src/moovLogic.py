from itertools import count
from sqlite3 import Timestamp
import threading
from typing import Text

from pymongo.common import RETRY_READS
from environmentProvider import EnvKeys
from issuesData import RelatedMotivationData
from issuesData import ConflictData
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

        self.userContextLock.acquire()
        try:
            if (userId in self.usersContext):
                userContextDetails = self.usersContext[userId]
                if ((datetime.datetime.utcnow() - userContextDetails.timeStamp) > datetime.timedelta(hours=12)):
                    self.usersContext.pop(userId)
                else: 
                    # print ("in setUserContextData - user context found and is ", userContextDetails.toJSON())
                    return userContextDetails
            
            # userId is not found / found and removed since TTL was breached
            userDetails = self.getUser(userId)
            userContextDetails = UserContextData(userId=userId, firstName=userDetails.firstName, lastName=userDetails.familyName, locale=userDetails.locale)

            userContextDetails.timeStamp = datetime.datetime.utcnow()
            self.usersContext[userId] = userContextDetails
        finally:
            self.userContextLock.release()

        print ('in setUserContextData - new user Context created and is ', userContextDetails.toJSON())
        return userContextDetails

    def getUserContextData(self, userId):
        
        # print ('in getUserContextData user id is ', userId)
        userContextDetails = None

        self.userContextLock.acquire()
        try:
            if (userId  in self.usersContext):
            
                userContextDetails = self.usersContext[userId]
            # print ('found user context and is ', userContextDetails.toJSON())
        finally:
            self.userContextLock.release()

        if (userContextDetails is None):
            userContextDetails = self.setUserContextData(userId)

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
            currMoovData = self.getBaseMoov(currMoov.moovId, userContext)

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

    def insertOrUpdateMotivation (self, motivationDataObj):
        self.dataBaseInstance.insertOrUpdateMotivation (motivationDataObj)

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

    def getBaseMoov (self, id, userContext: UserContextData):
        return self.dataBaseInstance.getBaseMoov(id=id, userContext=userContext)


    def getMoovsForIssueAndCounterpart (self, counterpartId, issueId, userContext: UserContextData):
        issueMoovs :list (IssueMoovData) = self.dataBaseInstance.getMoovsForIssueAndCounterpart(counterpartId=counterpartId, issueId=issueId, userContext=userContext)

        issueDetails = self.getIssue(issueId, userContext = None)

        extendedIssueMoovs = []

        for currMoov in issueMoovs:
            relatedMotivation = next((x for x in issueDetails.contributingMotivations if x.motivationId == currMoov.motivationId), None)
            
            if relatedMotivation is not None:
                currMoov.score = self.calculateIssueMoovScore(counterpartId=counterpartId, moov=currMoov, relatedMotivation=relatedMotivation)

            # create steps for moov
            extendedMoov = ExtendedIssueMoovData()
            extendedMoov.fromIssueMoov(currMoov)
            extendedMoov.steps = self.getStepsToMoov (currMoov)
            extendedIssueMoovs.append(extendedMoov)

        return extendedIssueMoovs

    def getStepsToMoov (self, moovData : BaseMoovData):
        moovSteps = moovData.howTo.split('*')

        if (moovSteps[0] == ''):
            # it might be that the first char is '*' - this creates an empty step
            del(moovSteps[0])

        return moovSteps


    def calculateIssueMoovScore (self, counterpartId, moov : IssueMoovData, relatedMotivation : RelatedMotivationData):
        userMotivationGap = self.getUserMotivationGap(userId=counterpartId, motivationId=relatedMotivation.motivationId) / ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase)

        multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        
        calculatedScore = 0
        calculatedScore += moov.score
        calculatedScore += relatedMotivation.impact 
        calculatedScore += multiplyer*userMotivationGap
        calculatedScore = moov.score + relatedMotivation.impact + multiplyer*userMotivationGap
        
        # normalize - get the % of 100
        normalizedScore = calculatedScore / (multiplyer*3) * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)
        return normalizedScore

    def calculateConflictMoovScore(self, moov : ConflictMoovData, conflictDetails : ConflictData):
        # return conflictDetails.score
        return moov.score

    def insertOrUpdateText (self, dataCollection, textDataObj):
        self.dataBaseInstance.insertOrUpdateText(dataCollection=dataCollection, textDataObj=textDataObj)
    
    def insertOrUpdateUserDetails (self, id, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, color = 0, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, color=color, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData):
        # get user details prior to potentially adding it to the DB
        existingUser = self.getUser(currUserData.id)

        if existingUser is None:
            currUserData.color = self.generateUserColor()
            currUserData.discoveryStatus = DiscoveryStatus.UNDISCOVERED

        self.dataBaseInstance.insertOrUpdateUser(currUserData=currUserData)

        if existingUser is None:
            #this is a new user - so we need to set a default password for him, and send a welcome email
            self.setUserPassword(userId=currUserData.id, passwordRaw=ep.getAttribute(EnvKeys.defaults, EnvKeys.initialUserPassword))
            self.notificationsProvider.sendWelcomeMail(userDetails=currUserData)

    def generateUserColor(self):
        return ep.generateRandomUserColor()

    def setMotivationsToUSer (self, id, motivations):
        self.dataBaseInstance.setMotivationsToUSer(id=id, motivations=motivations)

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
        userDetails : UserData = self.getUserByMail(mail=userMail)

        # TBD verify password
        # for now password is always true

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

    def setUserPassword (self, userId, passwordRaw):
        hashedPassword = hashlib.sha256(passwordRaw.encode('utf-8'))
        userCredDetails = UserCredData(id=userId, password=hashedPassword.hexdigest())

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
        moovInstancePriority = self.calculateConflictMoovPriority(userId, counterpartsIds)
        return self.dataBaseInstance.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, priority=moovInstancePriority, userContext=userContext)

    def extendAcctiveMoov(self, activeMoovId, newEndDate):
        activeMoovDetails = self.getActiveMoov(activeMoovId=activeMoovId)

        if (activeMoovDetails is not None):
            activeMoovDetails.plannedEndDate = newEndDate
            activeMoovDetails.isOverdue = False
            self.insertOrUpdateActiveMoov(activeMoovDetails=activeMoovDetails)

    def getActiveMoov (self, activeMoovId):
        return self.dataBaseInstance.getActiveMoov(id=activeMoovId)

    def insertOrUpdateActiveMoov(self, activeMoovDetails):
        self.dataBaseInstance.insertOrUpdateActiveMoov(activeMoov=activeMoovDetails)

    def calculateIssueMoovPriority(self, userId, counterpartId, motivationId):
        userRelationshipDetails : UserRelationshipData = self.getRelationshipData(userId=userId, counterpartId=counterpartId)

        if userRelationshipDetails is None:
            return ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority) / 2

        seperationQuestionsScale = ep.getAttribute(EnvKeys.behaviour,EnvKeys.seperationQuestionsScale)
        multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        
        calculatedPriority = multiplyer*userRelationshipDetails.seperationChanceEstimation/seperationQuestionsScale + multiplyer*userRelationshipDetails.costOfSeperation/seperationQuestionsScale + (multiplyer*self.getUserMotivationGap(userId=counterpartId, motivationId=motivationId)/ ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase))
        
        # normalize - get the % of 100
        normalizedPriorityValue = calculatedPriority / (multiplyer*3) * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)
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
            extendedMoovDetails.steps = self.getStepsToMoov(activeMoov.moovData)
            activeMoov.moovData = extendedMoovDetails

        return activeMoovs

    def getPastMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        return self.dataBaseInstance.getPastMoovsToCounterpart(userId=userId, counterpartDetails=counterpartDetails, userContext=userContext)

    def getActiveMoovsForUser (self, userId, userContext: UserContextData):
        activeMoovs = self.dataBaseInstance.getActiveMoovsForUser(userId=userId, userContext=userContext)

        #  calculate steps to moov
        for activeMoov in activeMoovs:
            extendedMoovDetails = ExtendedIssueMoovData() 
            extendedMoovDetails.fromBase(activeMoov.moovData)
            extendedMoovDetails.steps = self.getStepsToMoov(activeMoov.moovData)
            activeMoov.moovData = extendedMoovDetails

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

        usersToNotify += currUserPassivePOI
        usersToNotify.append(currUserDirectManager)        

        # notify to all who are interested in this user
        for userToNotify in usersToNotify:
            self.notificationsProvider.sendDiscoveryDoneMail(notifyTo=userToNotify, userWhoEndedDiscoveryDetails=currUser)    
    
    def getInterestedusers(self, userId):
        return self.dataBaseInstance.getInterestedUsers(userId)

    def insertOrUpdateRelationshipDetails (self, userId, counterpartId, costOfSeperation, chanceOfSeperation):
        relationshipDetails = UserRelationshipData(userId=userId, counterpartId=counterpartId, costOfSeperation=costOfSeperation, chanceOfSeperation=chanceOfSeperation, timestamp=datetime.datetime.utcnow())

        self.insertOrUpdateRelationship(relationshipDetails)

    def insertOrUpdateRelationship (self, relationshipData):
        self.dataBaseInstance.insertOrUpdateRelationship(relationshipData= relationshipData)

    def getRelationshipData (self, userId, counterpartId):
        return self.dataBaseInstance.getRelationshipData (userId=userId, counterpartId=counterpartId)

    def missingRelationshipData (self, userId, counterpartId):
        existingRelationShipData = self.getRelationshipData(userId=userId, counterpartId=counterpartId)

        missingRelationshipDataRetVal = True

        if (existingRelationShipData is not None):
            relationshipTimeSpan = datetime.timedelta(datetime.datetime.utcnow, existingRelationShipData.timestamp)
            if (relationshipTimeSpan < datetime.timedelta(days=ep.getAttribute(EnvKeys.behaviour, EnvKeys.relationshipDataTTLDays))):
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