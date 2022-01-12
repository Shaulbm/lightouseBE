import threading
from typing import Text

from pymongo.common import RETRY_READS
from environmentProvider import EnvKeys
from notificationsProvider import NotificationsProvider
from moovDB import MoovDBInstance
from generalData import UserData, UserPartialData, UserRoles, UserCircleData, Gender, Locale, UserContextData, UserCredData
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
            userContext = self.getuserContext(currMoov.userId)
            currMoovData = self.getBaseMoov(currMoov.moovId, userContext)

            userDetails = self.getUser(currMoov.userId)

            if (len(currMoov.counterpartIds) == 1):
                counterpartDetails = self.getUser(currMoov.counterpartIds[0])
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

    def getTextDataByParent (self, parentId, locale, gender):
        return self.dataBaseInstance.getTextDataByParent(parentId=parentId, locale=locale, gender=gender)

    def getTextDataByParents (self, parentsIds, locale, gender):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale, gender)

        return resultTextDict

    def insertOrUpdateMotivation (self, motivationDataObj):
        self.dataBaseInstance.insertOrUpdateMotivation (motivationDataObj)

    def insertOrUpdateMoov (self, moovDataObj):
        self.dataBaseInstance.insertOrUpdateMoov(moovDataObj)

    def insertOrUpdateConflictMoov (self, moovDataObj):
        self.dataBaseInstance.insertOrUpdateConflictMoov(moovDataObj)

    def getConflictMoovs (self, conflictId, userContext: UserContextData):
        return self.dataBaseInstance.getConflictMoovs (conflictId=conflictId, userContext=userContext)

    def getConflictsMoovsForUsers (self, teamMemberId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getConflictsMoovsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, userContext=userContext)

    def getIssueMoov (self, id, userContext: UserContextData):
        pass

    def getBaseMoov (self, id, userContext: UserContextData):
        return self.dataBaseInstance.getBaseMoov(id=id, userContext=userContext)


    def getMoovsForIssueAndUser (self, userId, issueId, userContext: UserContextData):
        return self.dataBaseInstance.getMoovsForIssueAndUser(userId=userId, issueId=issueId, userContext=userContext)

    def insertOrUpdateText (self, dataCollection, textDataObj):
        self.dataBaseInstance.insertOrUpdateText(self, dataCollection=dataCollection, textDataObj=textDataObj)
    
    def insertOrUpdateUserDetails (self, id, mail = "", parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData):
        # get user details prior to potentially adding it to the DB
        existingUser = self.getUser(currUserData.id)

        self.dataBaseInstance.insertOrUpdateUser(currUserData=currUserData)

        if existingUser is None:
            #this is a new user - so we need to set a default password for him, and send a welcome email
            self.setUserPassword(userId=currUserData.id, passwordRaw=ep.getAttribute(EnvKeys.defaults, EnvKeys.initialUserPassword))
            self.notificationsProvider.sendWelcomeMail(userDetails=currUserData)

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
        self.dataBaseInstance.getIssue(id= id, userContext=userContext)

    def insertOrUpdateConflict(self, currConflictData):
        self.insertOrUpdateConflict(currConflictData=currConflictData)

    def getConflict(self, id, userContext: UserContextData):
        return self.dataBaseInstance.getConflict

    def getConflictsForUsers (self, teamMemberId, counterpartId, partialData: bool, userContext : UserContextData):
        return self.dataBaseInstance.getConflictsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, partialData=partialData, userContext=userContext)

    def getIssuesForSubject (self, subjectId, userContext: UserContextData):
        return self.dataBaseInstance.getIssuesForSubject(subjectId=subjectId, userContext=userContext)
    
    def getAllIssues (self, userContext: UserContextData):
        return self.dataBaseInstance.getAllIssues(userContext=userContext)
    
    def getIssueForUser(self, issueId, userId, userContext: UserContextData):
        return self.dataBaseInstance.getIssueForUser(issueId=issueId, userId=userId, userContext=userContext)

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
            currentUserDetails = self.getUser(id=currPOI)
            peopleOfInterestList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, orgId=currentUserDetails.orgId, gender=currentUserDetails.gender, locale= currentUserDetails.locale, isRTL= currentUserDetails.isRTL, motivations=currentUserDetails.motivations))

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
        moovInstancePriority = self.calculateIssueMoovPriority(userId, counterpartId)
        return self.dataBaseInstance.activateIssueMoov(moovId=moovId, userId=userId, counterpartId=counterpartId, priority=moovInstancePriority, userContext=userContext)

    def activateConflictMoov (self, moovId, userId, counterpartsIds, userContext: UserContextData):
        moovInstancePriority = self.calculateConflictMoovPriority(userId, counterpartsIds)
        return self.dataBaseInstance.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, priority=moovInstancePriority, userContext=userContext)

    def calculateIssueMoovPriority(self, userId, caounterpartId):
        return 0

    def calculateConflictMoovPriority(self, userId, counterpartsIds):
        return 0

    def getActiveMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getActiveMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

    def getPastMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        return self.dataBaseInstance.getPastMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContext)

    def getActiveMoovsForUser (self, userId, userContext: UserContextData):
        return self.dataBaseInstance.getActiveMoovsForUser(userId=userId, userContext=userContext)

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId):
        return self.dataBaseInstance.getActiveMoovByMoovUserAndCounterpart (userId=userId, moovId=moovId, counterpartId=counterpartId)

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
        return self.dataBaseInstance.getInterestedusers(userId)