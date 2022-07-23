from imp import release_lock
from itertools import count
from sqlite3 import Timestamp
import threading
from tkinter.messagebox import NO
from typing import Text
from fastapi import HTTPException
import string
import random
import uuid
from pymongo.common import RETRY_READS
from environmentProvider import EnvKeys
from issuesData import RelatedMotivationData
from issuesData import ConflictData
from generalData import UserState
from generalData import AccountType
from moovData import MoovInstanceEvent, MoovInstanceEventTypes
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
import logging

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
        self.logger = logging.getLogger(__name__)

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

        insightsType = InsightsUserType.SELF_MANAGER

        if userDetails.role == UserRoles.EMPLOYEE:
            insightsType = InsightsUserType.SELF_EMPLOYEE

        insightsTypes = self.dataBaseInstance.getInsightsTypes (insightsType , userContext)

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

    def getMoovsForIssueAndCounterpart (self, userId, counterpartId, issueId, userContext: UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        issueMoovs :list (IssueMoovData) = self.dataBaseInstance.getMoovsForIssueAndCounterpart(counterpartDetails=counterpartDetails, issueId=issueId, userContext=userContext)

        issueDetails = self.getIssue(issueId, userContext = None)

        extendedIssueMoovs = []

        pastMoovs = self.getPastMoovsToCounterpart(userId = userId, counterpartId = counterpartId, userContext = userContext)
        activeMoovs = self.getActiveMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

        # filter arrays by issueId - improve performance
        pastMoovs = [pastMoov for pastMoov in pastMoovs if pastMoov.moovData.issueId == issueId]
        activeMoovs = [activeMoov for activeMoov in activeMoovs if activeMoov.moovData.issueId == issueId]

        for currMoov in issueMoovs:
            currMoov.score = self.calculateIssueMoovScore(counterpartId=counterpartId, moov=currMoov, pastMoovs= pastMoovs, activeMoovs=activeMoovs)

            # create steps for moov
            extendedMoov = ExtendedIssueMoovData()
            extendedMoov.fromIssueMoov(currMoov)
            extendedMoov.steps = self.getStepsToMoov (currMoov)
            extendedIssueMoovs.append(extendedMoov)

        return extendedIssueMoovs

    def doesMoovHaveRelevantInstances(self, pastMoovs, activeMoovs, moov):
        if (moov.issueId == ep.getAttribute(EnvKeys.moovs, EnvKeys.recommendedMoovsIssueId)):
            # this is a system recommendation issue, it's enough that he is currently having moovs from the same issue
            for activeMoov in activeMoovs:
                if activeMoov.moovData.issueId == moov.issueId:
                    return True
            
            relevantPastMoovs = [pastMoov for pastMoov in pastMoovs if pastMoov.moovData.issueId == moov.issueId]

            for pastMoov in relevantPastMoovs:
                # if there is a past moov with system recommendations started (as moovs can be opened with no limitation) less than the timeframe it's enough
                timeFromMoovEnd = datetime.datetime.utcnow() - pastMoov.startDate
                if timeFromMoovEnd.days < ep.getAttribute(EnvKeys.moovs, EnvKeys.pastMoovScorePenaltyForSystemRecommendationsDays):
                    return True
        else:
            for activeMoov in activeMoovs:
                # if the is an active moov with this id return true
                if activeMoov.moovId == moov.id:
                    return True

            relevantPastMoovs = [pastMoov for pastMoov in pastMoovs if pastMoov.moovId == moov.id]

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


    def calculateIssueMoovScore (self, counterpartId, moov : IssueMoovData, pastMoovs, activeMoovs):
        userMotivationGap = self.getUserMotivationGap(userId=counterpartId, motivationId=moov.motivationId) / ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase)

        multiplyer = ep.getAttribute(EnvKeys.behaviour, EnvKeys.priorityMultiplayer)
        gapBase = ep.getAttribute(EnvKeys.behaviour, EnvKeys.motivationGapBase)
        
        calculatedScore = 0
        calculatedScore = moov.score + multiplyer*userMotivationGap/gapBase
        
        # normalize - get the % of 100
        normalizedScore = calculatedScore / (multiplyer*2) * ep.getAttribute(EnvKeys.behaviour, EnvKeys.baseMoovPriority)
        if self.doesMoovHaveRelevantInstances(pastMoovs=pastMoovs, activeMoovs=activeMoovs, moov=moov):
            # if the moov was done in the last X days then the score should be penallize
            normalizedScore = normalizedScore * ep.getAttribute(EnvKeys.moovs, EnvKeys.moovInstanceScorePenaltyValue)

        return normalizedScore

    def calculateConflictMoovScore(self, moov : ConflictMoovData, conflictDetails : ConflictData):
        # return conflictDetails.score
        return moov.score

    def insertOrUpdateText (self, dataCollection, textDataObj):
        self.dataBaseInstance.insertOrUpdateText(dataCollection=dataCollection, textDataObj=textDataObj)
    
    def insertOrUpdateUserDetails (self, id, parentId = "", firstName = "", familyName = "", accountType = AccountType.REGULAR, gender = Gender.MALE, locale = Locale.UNKNOWN, color = 0, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, color=color, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData : UserData):
        self.dataBaseInstance.insertOrUpdateUser(currUserData=currUserData)

        # update cache that user was changed
        self.dbCache.setUserDirty(currUserData.id)

    def setUserDirty(self, userId):
        # update cache that should be reloaded
        self.dbCache.setUserDirty(userId) 

    def CreateUserWithDefaults ():
        pass

    def createUser (self, notifyNewUser = False, setDefaultPassword = False, parentId = "", firstName = "", familyName = "", accountType = AccountType.REGULAR ,gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = [], customMailTemplate=""):
        # get user details prior to potentially adding it to the DB
        existingUser = self.getUserByMail(mail=mailAddress)
        if (existingUser is not None):
            return existingUser.id

        userId = str(uuid.uuid4())
        newUser = UserData(id=userId, parentId=parentId, firstName=firstName, familyName= familyName, accountType=accountType, locale=locale, gender=gender, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        newUser.color = self.generateUserColor(newUser)
        newUser.discoveryStatus = DiscoveryStatus.UNDISCOVERED

        self.dataBaseInstance.insertOrUpdateUser(currUserData=newUser)

        userPassword = ""
        if (setDefaultPassword):
            userPassword = ep.getAttribute(EnvKeys.defaults, EnvKeys.initialUserPassword)
        else:
            userPassword = self.createRandomPassword()

        self.setUserPassword(userId=userId, orgId=newUser.orgId, passwordRaw = userPassword)

        if (notifyNewUser):
            self.notificationsProvider.sendWelcomeMail(userName=newUser.firstName, userMail=newUser.mailAddress, password=userPassword, customMailTemplate=customMailTemplate)

        return newUser.id

    def resetUserPassword(self, userMail):
       # get user details prior to potentially adding it to the DB
        existingUser = self.getUserByMail(userMail)

        if existingUser is None:
            return "user Not found"

        userPassword = self.createRandomPassword()
        self.setUserPassword(userId=existingUser.id, orgId=existingUser.orgId, passwordRaw = userPassword)
        self.notificationsProvider.sendResetPassword(userName=existingUser.firstName, userMail=existingUser.mailAddress, newPassword=userPassword)

        # update cache that user was changed
        self.dbCache.setUserDirty(existingUser.id)
        return "done"

    def createRandomPassword(self):
        # printing letters
        letters = string.ascii_letters
        

        # printing digits
        letters += string.digits

        #remove space from possible letters
        letters = letters.replace(" ","")
        newPassword = ( ''.join(random.choice(letters) for i in range(10)) )

        # select two special chars
        specialChars = '[@_!#$%^&*()<>?/\|}{~:]'
        specialCharA = random.choice(specialChars)
        specialCharB = random.choice(specialChars)
        strPos = random.randint(0, newPassword.__len__())
        newPassword = newPassword[:strPos] + specialCharA + newPassword[strPos:]
        strPos = random.randint(0, newPassword.__len__())
        newPassword = newPassword[:strPos] + specialCharB + newPassword[strPos:]

        return newPassword

    def verifyPasswordPolicy(self, password):
        if len(password) < 12:
            return False

        conditionsMet = 0

        # verify if contains Capital Letters:
        for char in password:
            if char.isupper():
                conditionsMet += 1
                break 

        # verify if contains non capital Letters:
        for char in password:
            if char.islower():
                conditionsMet += 1
                break 

        # verify if contains numbers:
        for char in password:
            if char.isdigit():
                conditionsMet += 1
                break 

        # verify if contains special characters:
        specialChars = '[@_!#$%^&*()<>?/\|}{~:]'
        for char in password:
            if char in specialChars:
                conditionsMet += 1
                break 

        if conditionsMet > 2:
            # we have met at least 3 conditions the password is valid
            return True

        return False

    def setUserDiscoveryStatus(self, userId, discoveryStatus):
        logger = logging.getLogger(__name__)
    
        logger.info('setUserDiscoveryStatus getting user details for user Id (0)', userId)
        userDetails = self.getUser(userId)

        if (userDetails is not None):
            logger.info('setUserDiscoveryStatus updating with discovery status (0)', discoveryStatus)          
            userDetails.discoveryStatus = discoveryStatus
            self.insertOrUpdateUser(userDetails)

    def generateUserColor(self, userDetails: UserData = None):

        if userDetails is None or userDetails.parentId == "":
            # either no user details or the user is currently no part of a team
            return ep.generateRandomUserColor()
        
        teamMates = self.getUsersUnder(userDetails.parentId, userContext = None)

        if len(teamMates) == 0:
            # no one in the team yet
            return ep.generateRandomUserColor()

        leftUserColors = ep.getAllUserColors()

        for currUser in teamMates:
            if currUser.color in leftUserColors:
                # remove colors that are currently in use in the team
                leftUserColors.remove(currUser.color)

        if len(leftUserColors) == 0:
            return ep.generateRandomUserColor()

        colorIdx = random.randint(0, len(leftUserColors)-1)
        return leftUserColors[colorIdx]

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
        # print ('in userLogin received mail #' + userMail +'# password #' + password + '#')

        userMail = userMail.lower().strip()
        password = password.strip()

        userDetails : UserData = self.getUserByMail(mail=userMail)

        partialUserDetails = None

        if (userDetails is not None and userDetails.state == UserState.ACTIVE):
            # print ('in user login, found user')

            hashedPassword = hashlib.sha256(password.encode('utf-8'))

            savedPassword = self.getUserPassword(userDetails.id)

            if  savedPassword != "" and savedPassword == hashedPassword.hexdigest():
                print ('in user login passwords match')
                partialUserDetails = UserPartialData()
                partialUserDetails.fromFullDetails(userDetails)
            else:
                # raise error 404
                # print ('in user login, passwords do not match')
                pass
        else:
            print ('in user login DID NOT found user or user is Inactive')

        if(partialUserDetails is not None):
            # update cache
            self.dbCache.setUserDirty(partialUserDetails.id) 

        return partialUserDetails

    def getUserPassword (self, userId):
        return self.dataBaseInstance.getUserPassword(userId=userId)

    def setUserPassword (self, userId,orgId, passwordRaw):
        hashedPassword = hashlib.sha256(passwordRaw.encode('utf-8'))
        userCredDetails = UserCredData(id=userId, orgId=orgId, password=hashedPassword.hexdigest())

        self.dataBaseInstance.setUserPassword(userCredDetails)

    def approvePrivacyPolicy(self, userContext: UserContextData):
        user = self.getUser(userContext.userId)

        user.privacyApprovalDate = datetime.datetime.utcnow()

        self.insertOrUpdateUser(user)

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

    def insertOrUpdateTrial(self, trialDetails):
        self.dataBaseInstance.insertOrUpdateTrial(trialDetails=trialDetails)

    def getIssue(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getIssue(id= id, userContext=userContext)

    def insertOrUpdateConflict(self, currConflictData):
        self.dataBaseInstance.insertOrUpdateConflict(currConflictData=currConflictData)

    def getConflict(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getConflict(id, userContext=userContext)

    def getConflictsForUsers (self, teamMemberId, counterpartId, partialData: bool, userContext : UserContextData):
        return self.dataBaseInstance.getConflictsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, partialData=partialData, userContext=userContext)
  
    def getAllIssues (self, counterpartId, userContext: UserContextData):
        issuesGender = userContext.gender
        if (counterpartId != ""):
            counterpartDetails = self.getUser(counterpartId)
            issuesGender = counterpartDetails.gender
            counterpartName = counterpartDetails.firstName
            
        return self.dataBaseInstance.getAllIssues(issuesGender= issuesGender, counterpartName = counterpartName, userContext=userContext)
    
    def getIssueForCounterpart(self, issueId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getIssueForCounterpart(issueId=issueId, counterpartId=counterpartId, userContext=userContext)

    def insertOrUpdateSubject(self, currSubjectData):
        self.dataBaseInstance.insertOrUpdateSubject(currSubjectData=currSubjectData)

    def getAllSubjects(self, userContext: UserContextData):
        return self.dataBaseInstance.getAllSubjects(userContext=userContext)

    def getUserCircle(self, userId, userContext: UserContextData):
        userCircleDetails = UserCircleData()
        userCircleDetails.teamMembersList = self.getUsersUnder(userId, userContext = userContext)
        userCircleDetails.peopleOfInterest = self.getUserPeopleOfInterest(userId, userContext = userContext)

        return userCircleDetails

    def getUsersUnder (self, userId, userContext : UserContextData):
        usersUnder = self.dataBaseInstance.getUsersUnder(userId=userId, userContext = userContext)

        if usersUnder == None:
            usersUnder = []
        
        for currUser in usersUnder:
            currUser.recommendedMoovsCount = self.getRecommendedMoovsAboveThresholdCount(userId=userId, counterpartId=currUser.id, userContext=userContext)

        return usersUnder

    def getUserPeopleOfInterest(self, userId, userContext: UserContextData):
        peopleOfInterestList = []

        requestingUser: UserData = self.getUser(id=userId)
        poiIdList = requestingUser.personsOfInterest 

        for currPOI in poiIdList:
            userPartialDetails = UserPartialData()
            userPartialDetails.fromFullDetails(self.getUser(id=currPOI))
            userPartialDetails.activeMoovsCount = self.dataBaseInstance.getActiveMoovsCountToCounterpart(userId=userId, counterpartId=userPartialDetails.id, userContext = userContext)
            userPartialDetails.recommendedMoovsCount = self.getRecommendedMoovsAboveThresholdCount(userId=userId, counterpartId=userPartialDetails.id, userContext = userContext)
            peopleOfInterestList.append (userPartialDetails)

        return peopleOfInterestList

    def getRecommendedMoovsAboveThresholdCount(self, userId, counterpartId, userContext: UserContextData):
        allRecommendedMoovs = self.getAllRecommendedMoovsForCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

        recommendedMoovsThreshold = ep.getAttribute(EnvKeys.moovs, EnvKeys.topRecommendedMoovThreshold)

        recommendedMoovsAboveThreshold = [rm for rm in allRecommendedMoovs if rm.score > recommendedMoovsThreshold]

        return recommendedMoovsAboveThreshold.__len__()


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
        activeMoov = self.dataBaseInstance.activateIssueMoov(moovId=moovId, userId=userId, counterpartId=counterpartId, priority=moovInstancePriority, userContext=userContext)

        activeMoov = self.addSystemEventToMoovInstance(moovInstanceId=activeMoov.id, eventType=MoovInstanceEventTypes.LIFETIME_START)

        return activeMoov

    def activateConflictMoov (self, moovId, userId, counterpartsIds, userContext: UserContextData):
        # moovInstancePriority = self.calculateConflictMoovPriority(userId, counterpartsIds)
        # return self.dataBaseInstance.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, priority=moovInstancePriority, userContext=userContext)
        pass

    def extendActiveMoov(self, activeMoovId, userContext:UserContextData):
        self.addSystemEventToMoovInstance(moovInstanceId=activeMoovId, eventType=MoovInstanceEventTypes.LIFETIME_EXTENTION)

        activeMoovDetails = self.getActiveMoov(activeMoovId=activeMoovId, userContext= None)

        if (activeMoovDetails is not None):
            activeMoovDetails.plannedEndDate = datetime.datetime.utcnow() + datetime.timedelta(days=ep.getAttribute(EnvKeys.moovs, EnvKeys.extendActiveMoovTimeDays))
            activeMoovDetails.isOverdue = False
            self.insertOrUpdateActiveMoov(activeMoovDetails=activeMoovDetails)

        # not great design - I know - first getActiveMoov will not translate the system events - this is why we can save it again 
        activeMoovDetails = self.getActiveMoov(activeMoovId=activeMoovId, userContext= userContext)
        return activeMoovDetails

    def getActiveMoov (self, activeMoovId, userContext: UserContextData):
        return self.dataBaseInstance.getActiveMoov(id=activeMoovId, userContext=userContext)

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

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId, userContext:UserContextData):
        activeMoov = self.dataBaseInstance.getActiveMoovByMoovUserAndCounterpart (userId=userId, moovId=moovId, counterpartId=counterpartId, userContext=userContext)

        #  calculate steps to moov
        extendedMoovDetails = ExtendedIssueMoovData() 
        extendedMoovDetails.fromBase(activeMoov.moovData)
        extendedMoovDetails.steps = self.getStepsToMoov(activeMoov.moovData)
        activeMoov.moovData = extendedMoovDetails 

        return activeMoov

    def endMoov (self, activeMoovId, feedbackScore, feedbackText, isEndedByTimer):
        self.addUserFeedbackEventToMoovInstance(moovInstanceId = activeMoovId, text=feedbackText, score = feedbackScore)
        self.addSystemEventToMoovInstance(moovInstanceId=activeMoovId, eventType=MoovInstanceEventTypes.LIFETIME_END)

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
        
        # this will switch the chance of seperation from 1..5 to 5..1
        calculatedChanceOfSeperation = ((chanceOfSeperation-1)*(-1)) + 5

        relationshipDetails = UserRelationshipData(userId=userId, counterpartId=counterpartId, costOfSeperation=costOfSeperation, chanceOfSeperation=calculatedChanceOfSeperation, timeStamp=datetime.datetime.utcnow())

        self.insertOrUpdateRelationship(relationshipDetails)

    def getTrialDetails(self, trialId):
        return self.dataBaseInstance.getTrialDetails(trialId)

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
        allRecommendedMoovs = self.getAllRecommendedMoovsForCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

        sortedRecommendedMoovs = sorted(allRecommendedMoovs, key=lambda x: x.score, reverse=True)

        topRecommendedMoovsToReturn = ep.getAttribute(EnvKeys.moovs, EnvKeys.topRecommendedMoovsNo)
        recommendedMoovsThreshold = ep.getAttribute(EnvKeys.moovs, EnvKeys.topRecommendedMoovThreshold)

        topRecommendedMoovs = sortedRecommendedMoovs[:topRecommendedMoovsToReturn]

        # remove recommended moovs with score lesser than threshold
        topRecommendedMoovs = [rm for rm in topRecommendedMoovs if rm.score > recommendedMoovsThreshold]

        return topRecommendedMoovs 
        
    def getAllRecommendedMoovsForCounterpart(self, userId, counterpartId, userContext: UserContextData):
        recommendedMoovs = self.getMoovsForIssueAndCounterpart(userId=userId, counterpartId=counterpartId, issueId=ep.getAttribute(EnvKeys.moovs, EnvKeys.recommendedMoovsIssueId), userContext=userContext)

        return recommendedMoovs

    def setNameInText (self, text, name):
        tempText = text.replace("<<NAME>>", name)
        tempText = tempText.replace("<<>>", name)
        tempText = tempText.replace("<< >>", name)

        return tempText

    def updateUserDetails(self, id, locale, gender, presentFullHierarchy):
        userDetails = self.getUser(id)

        if (userDetails is None):
            raise HTTPException(status_code=404, detail="user not found")

        userDetails.locale = locale
        userDetails.gender = gender
        userDetails.presentFullHierarchy = presentFullHierarchy

        self.insertOrUpdateUser(userDetails)

        return userDetails

    def updateUserPassword(self, id, oldPassword, newPassword):
        userDetails = self.getUser(id)

        if (userDetails is None):
            raise HTTPException(status_code=404, detail="user not found")

        #verify old password
        savedPassword = self.getUserPassword(userDetails.id)
        hashedOldPassword = hashlib.sha256(oldPassword.encode('utf-8'))
        if  savedPassword != "" and savedPassword != hashedOldPassword.hexdigest():
            print ('in updateUserPassword ole password do not match user is {0}', userDetails.mailAddress)
            raise HTTPException(status_code=401, detail="old password do not match")
        
        # verify password policy
        if self.verifyPasswordPolicy(newPassword):
            self.setUserPassword(userId=id, orgId=userDetails.orgId, passwordRaw=newPassword)
            return ""
        else:
            raise HTTPException(status_code=401, detail="wrong password policy")

    def sendUserFeedback(self, userId, issue, text):
        userDetails = self.getUser(userId)
        return self.notificationsProvider.sendUserFeedback(userId=userId, userMail=userDetails.mailAddress, issue=issue, text=text)

    def sendDiscoveryReminder(self, counterpartId, userContext : UserContextData):
        counterpartDetails = self.getUser(counterpartId)
        return self.notificationsProvider.sendDiscoveryReminder(notifyToMail=counterpartDetails.mailAddress, notifyToName=counterpartDetails.firstName, teamManagerName=userContext.firstName)

    def addUserFeedbackEventToMoovInstance(self, moovInstanceId, text, score):
        moovInstanceEvent = MoovInstanceEvent(timeStamp=datetime.datetime.utcnow(), type=MoovInstanceEventTypes.FEEDBACK, content=text, score=score)
        return self.addEventToMoovInstance(moovInstanceId=moovInstanceId, moovInstanceEvent=moovInstanceEvent)

    def verifyUserEventChangePermission(self, activeMoovId, userId) -> bool:
        activeMoovDetails = self.getActiveMoov(activeMoovId=activeMoovId, userContext=None)

        if (activeMoovDetails):
            if (activeMoovDetails.userId == userId):
                return True

        print ('verifyUserEventChangePermission received request to add event to activeMoovId {0} but from userId {1} which is not the owner ', activeMoovId, userId)
        return False

    def addUserEventToMoovInstance(self, moovInstanceId, text, userContext = UserContextData):
        moovInstanceEvent = MoovInstanceEvent(timeStamp=datetime.datetime.utcnow(), type=MoovInstanceEventTypes.USER_COMMENT, content=text)
        self.addEventToMoovInstance(moovInstanceId=moovInstanceId, moovInstanceEvent=moovInstanceEvent)
        
        # there are elements of localization that requires to get the data AFTER the event was added to the db.
        return self.getActiveMoov(moovInstanceId, userContext=userContext)

    def addSystemEventToMoovInstance(self, moovInstanceId, eventType):
        text = self.getTextIdForType(eventType=eventType)
        moovInstanceEvent = MoovInstanceEvent(timeStamp=datetime.datetime.utcnow(), type=eventType, content=text)
        return self.addEventToMoovInstance(moovInstanceId=moovInstanceId, moovInstanceEvent=moovInstanceEvent)

    def addEventToMoovInstance(self, moovInstanceId, moovInstanceEvent):
        moovInstance = self.getActiveMoov(moovInstanceId, userContext=None)

        if moovInstance is None:
            return
        
        moovInstance.events.append(moovInstanceEvent)
        self.insertOrUpdateActiveMoov(moovInstance)

        return moovInstance

    def getTextIdForType(self, eventType):
        switcher = {
            MoovInstanceEventTypes.LIFETIME_START: "SYS_TXT_MIE_001",
            MoovInstanceEventTypes.LIFETIME_END: "SYS_TXT_MIE_002",
            MoovInstanceEventTypes.LIFETIME_EXTENTION: "SYS_TXT_MIE_003"
        }
        
        return switcher.get(eventType, "")