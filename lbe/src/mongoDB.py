from hashlib import new
from threading import current_thread
import threading
from typing import Text
from anytree.node import nodemixin
from pymongo import MongoClient
from pymongo.common import partition_node
from moovData import MoovData
from motivationsData import MotivationData, MotivationPartialData
from generalData import UserData, UserPartialData, UserRoles, UserCircleData, Gender, Locale, UserImageData, UserContextData
from questionsData import QuestionData
from singleton import Singleton
from discoveryData import UserDiscoveryJourneyData, DiscoveryBatchData
from loguru import logger
import anytree
from anytree import Node
from issuesData import IssueData, SubjectData, IssuePartialData, IssueExtendedData, ActiveMoov, ExtendedActiveMoov
import datetime

LOCALE_HEB_MA = 1
LOCALE_HEB_FE = 2
LOCALE_EN = 3


class moovDBInstance(metaclass=Singleton):
    def __init__(self):
        self.dataBaseInstance = None
        self.counterLock = threading.Lock()
        self.usersContext = {}

    def lock(self):
        self.counterLock.acquire()

    def release(self):
        self.counterLock.release()

    def setUserContextData(self, userId):
        if (userId in self.usersContext):
            userContextDetails = self.usersContext[userId]
            if ((datetime.datetime.utcnow() - userContextDetails.timeStamp) > datetime.timedelta(hours=12)):
                self.usersContext.pop(userId)
            else: 
                print ("in setUserContextData - user context found and is ", userContextDetails.toJSON())
                return userContextDetails
        
        # userId is not found / found and removed
        userDetails = self.getUser(userId)
        userContextDetails = UserContextData(userId=userId, firstName=userDetails.firstName, lastName=userDetails.familyName, locale=userDetails.locale)

        userContextDetails.timeStamp = datetime.datetime.utcnow()
        self.usersContext[userId] = userContextDetails

        print ('in setUserContextData - user Context created and is ', userContextDetails.toJSON())
        return userContextDetails

    def getUserContextData(self, userId):
        
        print ('in getUserContextData user id is ', userId)
        userContextDetails = None

        if (userId  in self.usersContext):
            
            userContextDetails = self.usersContext[userId]
            print ('found user context and is ', userContextDetails.toJSON())

        return userContextDetails

    def getDatabase(self):

        if (self.dataBaseInstance is None):
            connectionString = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
            client = MongoClient(connectionString)
            self.dataBaseInstance = client.moov

        return self.dataBaseInstance

    def getNextCount(self):
        db = self.getDatabase()
        counterCollection = db["counter"]

        counterValue = 0
        self.counterLock.acquire()

        try:
            counterFilter = {"id" : "COUNTER"}
            #find Counter, if not exist create new. if exist get value and update.
            counterData = counterCollection.find_one(counterFilter)
            if (counterData is None):
                counterCollection.insert_one({"id": "COUNTER", "val": counterValue+1})
            else:
                counterValue = int(counterData["val"])
                counterCollection.replace_one (counterFilter, {"id": "COUNTER","val": counterValue+1})
        finally:
            self.counterLock.release()

        return counterValue

    def getTextDataByParent (self, parentId, locale):
        textDataCollection = self.getTextCollectionByLocale(locale)
            
        allTextsArray = textDataCollection.find ({"parentId" : parentId})

        textDic = {}

        for currText in allTextsArray:
            textDic[currText["id"]] = currText["text"]

        return textDic

    def getTextDataByParents (self, parentsIds, locale):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale)

        return resultTextDict


    def getTextCollectionByLocale(self, locale):
        db = self.getDatabase()

        if locale == LOCALE_HEB_FE:
            return db["locale_he_fe"]
        elif locale == LOCALE_HEB_MA:
            return db["locale_he_ma"]
        elif locale == LOCALE_EN:
            return db["locale_en"]
        else:
            return db ["locale_en"]

    def insertOrUpdateMotivation (self, dataCollection, motivationDataObj):
        motivationDataJSON = dataCollection.find_one({"id" : motivationDataObj.id})

        if (motivationDataJSON is not None):
            #object found
            motivationFilter = {'id':motivationDataObj.id}
            dataCollection.replace_one (motivationFilter, motivationDataObj.toJSON())
        else:
            # this is a new motivation
            dataCollection.insert_one(motivationDataObj.toJSON())

    def insertOrUpdateMoov (self, moovDataObj):
        db = self.getDatabase()
        moovsCollection = db["moovs"]
        moovDataJSON = moovsCollection.find_one({"id" : moovDataObj.id})

        if (moovDataJSON is not None):
            #object found
            moovFilter = {'id':moovDataObj.id}
            moovsCollection.replace_one (moovFilter, moovDataObj.toJSON())
        else:
            # this is a new moov
            moovsCollection.insert_one(moovDataObj.toJSON())

    def getMoov (self, id, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        moovDataJSON = moovsCollection.find_one({"id" : id})

        if (moovDataJSON is None):
            return None

        moovTextsDic = None
        if (userContext.locale is not None):
            moovTextsDic = self.getTextDataByParent(id, userContext.locale)

        newMoov = MoovData()
        newMoov.buildFromJSON(moovDataJSON, moovTextsDic)

        return newMoov 

    def getMoovsForIssueAndUser (self, userId, issueId, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]
        requestedUser = self.getUser(userId)

        if (requestedUser.motivations is None or requestedUser.motivations.__len__ == 0):
            return {}

        userMotivationsIds = list(requestedUser.motivations.keys())

        moovFilter = {"issueId":issueId,"motivationId": {"$in":userMotivationsIds}}
        motivationsDataJSONList = moovsCollection.find(moovFilter)

        if (motivationsDataJSONList is None):
            return None

        foundMoovs = []
        for currMoovJSONData in motivationsDataJSONList:
            moovTextsDic = self.getTextDataByParent(currMoovJSONData["id"], userContext.locale)
            newMoov = MoovData()
            newMoov.buildFromJSON(currMoovJSONData, moovTextsDic)
            foundMoovs.append(newMoov)

        return foundMoovs

    def insertOrUpdateText (self, dataCollection, textDataObj):
        textDataJSON = dataCollection.find_one({"id" : textDataObj.id})

        if (textDataJSON is not None):
            #object found
            textDataFilter = {'id' : textDataObj.id}
            dataCollection.replace_one(textDataFilter, textDataObj.toJSON())
        else:
            # this is a new motivation
            dataCollection.insert_one(textDataObj.toJSON())
    
    def insertOrUpdateUserDetails (self, id, mail = "", parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, orgId=orgId, role=role, mailAddress=mail, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData):
        db = self.getDatabase()
        usersCollection = db["users"]

        foundUser = usersCollection.find_one({"id":currUserData.id})

        if (foundUser is not None):
            #the user already exists - update the user
            userDataFilter = {"id" : currUserData.id}
            usersCollection.replace_one(userDataFilter, currUserData.toJSON())
        else:
            #this is a new user
            usersCollection.insert_one(currUserData.toJSON())

    def setMotivationsToUSer (self, id, motivations):
        userDetails = self.getUser(id=id)

        if (userDetails is None):
            # user not found
            return None

        userDetails.motivations = motivations.copy()
        userFilter = {"id":id}

        db = self.getDatabase()
        usersCollection = db["users"]

        usersCollection.replace_one(userFilter, userDetails.toJSON())

        return userDetails

    def getMotivation (self, id, userContext: UserContextData):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        motivationDataJSON = motivationCollection.find_one({"id" : id})

        if (motivationDataJSON is None):
            return None

        # print ("motivation data is {0}", motivationDataJSON)

        motivationTextsDic = self.getTextDataByParent(id, userContext.locale)

        newMotivtion = MotivationData()
        newMotivtion.buildFromJSON(motivationDataJSON, motivationTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return newMotivtion 
    
    def getAllMotivations(self,userContext:UserContextData):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        motivationsDataJSONList = motivationCollection.find()

        if (motivationsDataJSONList is None):
            return None

        foundMotivations = []
        for currMotivationJSONData in motivationsDataJSONList:
            motivationTextsDic = self.getTextDataByParent(currMotivationJSONData["id"], userContext.locale)
            newMotivation = MotivationPartialData()
            newMotivation.buildFromJSON(currMotivationJSONData, motivationTextsDic)
            foundMotivations.append(newMotivation)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return foundMotivations 

    def getUserMotivations (self, userId, userContext:UserContextData):
        db = self.getDatabase()
        motivationCollection = db["motivations"]
        requestedUser = self.getUser(userId)

        if (requestedUser.motivations is None or requestedUser.motivations.__len__ == 0):
            return {}

        motivationsIds = list(requestedUser.motivations.keys())

        motivationsFilter = {"id": {"$in":motivationsIds}}
        motivationsDataJSONList = motivationCollection.find(motivationsFilter)

        if (motivationsDataJSONList is None):
            return None

        foundMotivations = []
        for currMotivationJSONData in motivationsDataJSONList:
            motivationTextsDic = self.getTextDataByParent(currMotivationJSONData["id"], userContext.locale)
            newMotivation = MotivationPartialData()
            newMotivation.buildFromJSON(currMotivationJSONData, motivationTextsDic)
            foundMotivations.append(newMotivation)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return foundMotivations 


    def getAllMotivationsIds(self):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        foundMotivations = motivationCollection.find({})

        motivationsIds = []
    
        if (foundMotivations is not None):
            motivationsIds = [m["id"] for m in foundMotivations]

        return motivationsIds

    def userLogin(self, userMail, password):
        userDetails = self.getUser(mail=userMail)

        # TBD verify password
        # for now password is always true

        partialUserDetails = None

        if (userDetails is not None):
            partialUserDetails = UserPartialData()
            partialUserDetails.fromFullDetails(userDetails)
        
        return partialUserDetails

    def getUser (self, id = "", mail = ""):
        db = self.getDatabase()
        usersCollection = db["users"]

        userFilter = {}

        if (id != ""): 
            userFilter = {"id":id}
        elif (mail != ""):
            userFilter = {"mailAddress":mail}
        else:
            # no identifier is passed to the user
            return None

        userDataJSON = usersCollection.find_one(userFilter)

        if (userDataJSON is None):
            #no user found
            return None

        userDetails = UserData()
        userDetails.fromJSON(userDataJSON)

        return userDetails

    def insertOrUpdateQuestion(self, currQuestionData):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        foundQuestion = questionsCollection.find_one({"id":currQuestionData.id})

        if (foundQuestion is not None):
            #the user already exists - update the user
            questionDataFilter = {"id" : currQuestionData.id}
            questionsCollection.replace_one(questionDataFilter, currQuestionData.toJSON())
        else:
            #this is a new user
            questionsCollection.insert_one(currQuestionData.toJSON())

    def getQuestion(self, id, userContext: UserContextData):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        questionsDataJSON = questionsCollection.find_one({"id" : id})

        if (questionsDataJSON is None):
            return None

        questionTextsDic = None
        
        print ('in getQuestion user Context is ', userContext.toJSON())

        if (userContext.locale != Locale.UNKNOWN):
            # get id's for text quesry
            parentsIds = ([p["id"] for p in questionsDataJSON["possibleResponses"]])
            parentsIds.append(questionsDataJSON["id"])
            
            # get localed text
            questionTextsDic = self.getTextDataByParents(parentsIds, userContext.locale)

        questionDetails = QuestionData()
        questionDetails.buildFromJSON(questionsDataJSON, questionTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return questionDetails

    def getQuestionsFromBatch(self, batchId, userContext:UserContextData):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        questionsDataJSON = questionsCollection.find({"batchId" : batchId})

        if (questionsDataJSON is None):
            return None        

        questionsInBatch = []

        for currQuestion in questionsDataJSON:
            questionsInBatch.append (self.getQuestion(currQuestion["id"], userContext))

        return questionsInBatch

    def getUserDiscoveryJourney(self, userId):
        db = self.getDatabase()
        discoveryJourneyCollection = db["userDiscoveryJourney"]

        userFilter = {"userId":userId}

        discoveryJourneyDataJSON = discoveryJourneyCollection.find_one(userFilter)

        if (discoveryJourneyDataJSON is None):
            #no discovery journey data found
            return None

        userDiscoveryDetails = UserDiscoveryJourneyData()
        userDiscoveryDetails.buildFromJSON(discoveryJourneyDataJSON)

        return userDiscoveryDetails

    def insertOrUpdateDiscoveryJourney(self, discoveryJourneyData):
        db = self.getDatabase()
        discoveryJourneyCollection = db["userDiscoveryJourney"]

        foundDiscoveryJourney = discoveryJourneyCollection.find_one({"id":discoveryJourneyData.id})

        if (foundDiscoveryJourney is not None):
            #the user already exists - update the user
            questionDataFilter = {"id" : discoveryJourneyData.id}
            discoveryJourneyCollection.replace_one(questionDataFilter, discoveryJourneyData.toJSON())
        else:
            #this is a new user
            discoveryJourneyCollection.insert_one(discoveryJourneyData.toJSON())

    def getDiscvoeryBatch(self, userContext: UserContextData, batchId = "", journeyId = "", batchIdx = ""):
        db = self.getDatabase()
        discoveryJourneyCollection = db["discoveryData"]

        userFilter = {}

        if (batchId != ""):
            userFilter = {"batchId" : batchId}
        elif (batchIdx != ""):
            userFilter = {"journeyId":journeyId, "batchIdx":batchIdx}
        else:
            #both bathId and BatchIdx are empty - this is the first Batch
            userFilter = {"journeyId":journeyId, "batchIdx":1}

        discoveryBatchDataJSON = discoveryJourneyCollection.find_one(userFilter)

        if (discoveryBatchDataJSON is None):
            #no discovery journey data found
            return None

        localedTextDict = self.getTextDataByParent(discoveryBatchDataJSON["batchId"], userContext.locale)

        discoveryBatchDetails = DiscoveryBatchData()
        discoveryBatchDetails.buildFromJSON(discoveryBatchDataJSON, localedTextDict)

        return discoveryBatchDetails   

    def insertOrUpdateIssue(self, currIssueData):
        db = self.getDatabase()
        issuesCollection = db["issues"]

        foundIssue = issuesCollection.find_one({"id":currIssueData.id})

        if (foundIssue is not None):
            #the issue already exists - update the issue
            questionDataFilter = {"id" : currIssueData.id}
            issuesCollection.replace_one(questionDataFilter, currIssueData.toJSON())
        else:
            #this is a new user
            issuesCollection.insert_one(currIssueData.toJSON())

    def getIssue(self, id, userContext: UserContextData):
        db = self.getDatabase()
        issuesCollection = db["issues"]

        issueDataJSON = issuesCollection.find_one({"id" : id})

        if (issueDataJSON is None):
            return None

        issuesTextsDic = None
        
        if (userContext.locale != Locale.UNKNOWN):
            # get id's for text quesry
            parentsIds = []
            parentsIds.append(issueDataJSON["id"])
            parentsIds = parentsIds + ([p["id"] for p in issueDataJSON["contributingMotivations"]])
            parentsIds = parentsIds + ([p["id"] for p in issueDataJSON["resolvingMotivations"]]) 
            

            # get localed text
            issuesTextsDic = self.getTextDataByParents(parentsIds, userContext.locale)

        issueDetails = IssueData()
        issueDetails.buildFromJSON(jsonData = issueDataJSON, localedTextDic=issuesTextsDic)

        return issueDetails

    def getIssuesForSubject (self, subjectId, userContext: UserContextData):
        db = self.getDatabase()
        subjectsCollection = db["issues"]

        dataFilter = {"subjectId": subjectId}

        issuesDataJSONList = subjectsCollection.find(dataFilter)

        issuesDetailsList = []

        for currIssueJSONData in issuesDataJSONList:
            issueTextsDic = self.getTextDataByParent(currIssueJSONData["id"], userContext.locale)
            newIssue = IssuePartialData()
            newIssue.buildFromJSON(currIssueJSONData, issueTextsDic)
            issuesDetailsList.append(newIssue)        

        return issuesDetailsList
    
    def getAllIssues (self, userContext: UserContextData):
        db = self.getDatabase()
        subjectsCollection = db["issues"]

        issuesDataJSONList = subjectsCollection.find()

        issuesDetailsList = []

        for currIssueJSONData in issuesDataJSONList:
            issueTextsDic = self.getTextDataByParent(currIssueJSONData["id"], userContext.locale)
            newIssue = IssuePartialData()
            newIssue.buildFromJSON(currIssueJSONData, issueTextsDic)
            issuesDetailsList.append(newIssue)        

        return issuesDetailsList
    
    def getIssueForUser(self, issueId, userId, userContext: UserContextData):

        issueDetails = self.getIssue (id=issueId, userContext=userContext)
        userDetails = self.getUser(id=userId)

        # filter all the resolving motivations that are in the user motivations
        filteredResolvingMotivatios = [rm for rm in issueDetails.resolvingMotivations if rm.motivationId in userDetails.motivations]
        filteredContributingMotivatios = [cm for cm in issueDetails.contributingMotivations if cm.motivationId in userDetails.motivations]

        issueDetails.resolvingMotivations = filteredResolvingMotivatios.copy()
        issueDetails.contributingMotivations = filteredContributingMotivatios.copy()

        issueExtendedDetails = IssueExtendedData()
        issueExtendedDetails.copyFromBaseClass(issueDetails)

        #prepare motviations names
        allMotivations = self.getAllMotivations(userContext)
        motivationsNameDict = {x.id:x.name for x in allMotivations}

        #copy Motivations names
        for currRelatedMotivation in issueExtendedDetails.contributingMotivations:
            currRelatedMotivation.motivationName = motivationsNameDict[currRelatedMotivation.motivationId]

        for currRelatedMotivation in issueExtendedDetails.resolvingMotivations:
            currRelatedMotivation.motivationName = motivationsNameDict[currRelatedMotivation.motivationId]

        return issueExtendedDetails

    def insertOrUpdateSubject(self, currSubjectData):
        db = self.getDatabase()
        subjectsCollection = db["subjects"]

        foundIssue = subjectsCollection.find_one({"id":currSubjectData.id})

        if (foundIssue is not None):
            #the issue already exists - update the issue
            questionDataFilter = {"id" : currSubjectData.id}
            subjectsCollection.replace_one(questionDataFilter, currSubjectData.toJSON())
        else:
            #this is a new user
            subjectsCollection.insert_one(currSubjectData.toJSON())

    def getAllSubjects(self, userContext: UserContextData):
        db = self.getDatabase()
        subjectsCollection = db["subjects"]

        subjectsDataJSONList = subjectsCollection.find()

        if (subjectsDataJSONList is None):
            return None

        foundSubjects = []
        for currSubjectJSONData in subjectsDataJSONList:
            subjectTextsDic = self.getTextDataByParent(currSubjectJSONData["id"], userContext.locale)
            newSubject = SubjectData()
            newSubject.buildFromJSON(currSubjectJSONData, subjectTextsDic)
            foundSubjects.append(newSubject)

        return foundSubjects

    def getUserCircle(self, userId):
        db = self.getDatabase()

        print ('in getUserCircle, UserID is {0}', userId)

        userCircleDetails = UserCircleData()
        userCircleDetails.teamMembersList = self.getUsersUnder(userId)

        print ('in getUserCircle, after team members')
        
        userCircleDetails.peopleOfInterest = self.getUserPeopleOfInterest(userId)
        print ('in getUserCircle, after team poi')

        return userCircleDetails

    def getUsersUnder (self, userId):
        requestingUser = self.getUser(id=userId)

        foundSubordinatesDataList = []

        if (requestingUser is None):
            return None

        db = self.getDatabase()
        usersCollection = db["users"]

        if (requestingUser.orgId is None or requestingUser.orgId == ""):
            return None

        # get all users in the user organization
        foundUsers = usersCollection.find({"orgId":requestingUser.orgId})

        if (foundUsers is None):
            # no users in the organization
            return foundSubordinatesDataList

        # if the currentUser is HR return all org
        if (requestingUser.role == UserRoles.HR):
            # this is the HR of the organization - return a list of all the employees in the organization
            for currentFoundUser in foundUsers:
                currentUserDetails = UserData()
                currentUserDetails.fromJSON(currentFoundUser)

                if (currentUserDetails.id != requestingUser.id):
                    foundSubordinatesDataList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, gender=currentUserDetails.gender, locale= currentUserDetails.locale, isRTL= currentUserDetails.isRTL, orgId=currentUserDetails.orgId, motivations=currentUserDetails.motivations))

            return foundSubordinatesDataList

        # the requesting user is not the HR, find all the users under this user
        rootNode = Node('root')
        requestingUserNode = None

        # for each user in the organization
        for currentFoundUser in foundUsers:
            currentUserDetails = UserData()
            currentUserDetails.fromJSON(currentFoundUser)
            
            currentUserNode = anytree.search.find_by_attr(rootNode, currentUserDetails.id)
            currentUserParentNode = anytree.search.find_by_attr(rootNode, currentUserDetails.parentId)

            if (currentUserParentNode is None):
                #this is the first time we find this Id
                currentUserParentNode = Node(currentUserDetails.parentId, rootNode)
            
            if (currentUserNode is None):
                #this is the first time we find this Id
                currentUserNode = Node (currentUserDetails.id, currentUserParentNode)
            else:
                # this user Id is already in the tree
                currentUserNode.parent = currentUserParentNode

            if (currentUserDetails.id == userId):
                #this is the user that we want to get all his subordinates
                requestingUserNode = currentUserNode

        # now we have the organization hierarchy, get the list of all this managers subordinates
        foundSubordinates = anytree.search.findall(requestingUserNode)

        if (foundSubordinates is not None):
            foundSubordinatesList = list(foundSubordinates)
            for currentSubordinate in foundSubordinatesList:
                if (currentSubordinate.name != requestingUser.id):
                    #the manager is also part of the nodes list and should be ignored
                    currentUserDetails = self.getUser(id=currentSubordinate.name)
                    foundSubordinatesDataList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, gender=currentUserDetails.gender, locale= currentUserDetails.locale, isRTL= currentUserDetails.isRTL, orgId=currentUserDetails.orgId, motivations=currentUserDetails.motivations))

        return foundSubordinatesDataList

    def getUserPeopleOfInterest(self, userId):
        peopleOfInterestList = []

        requestingUser = self.getUser(id=userId)
        poiIdList = requestingUser.personsOfInterest 

        for currPOI in poiIdList:
            currentUserDetails = self.getUser(id=currPOI)
            peopleOfInterestList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, orgId=currentUserDetails.orgId, gender=currentUserDetails.gender, locale= currentUserDetails.locale, isRTL= currentUserDetails.isRTL, motivations=currentUserDetails.motivations))

        return peopleOfInterestList

    def insertOrUpdateUserImage(self, imageData):
        db = self.getDatabase()
        usersImagesCollection = db["usersImages"]

        foundImage = usersImagesCollection.find_one({"userId":imageData.userId})

        if (foundImage is not None):
            #the issue already exists - update the issue
            imageDataFilter = {"id" : imageData.userId}
            usersImagesCollection.replace_one(imageDataFilter, imageData.toJSON())
        else:
            #this is a new user
            usersImagesCollection.insert_one(imageData.toJSON())

    def getUserImage(self, userId):
        db = self.getDatabase()
        usersImagesCollection = db["usersImages"]

        userFilter = {"userId":userId}

        userImageDataJSON = usersImagesCollection.find_one(userFilter)

        if (userImageDataJSON is None):
            #no discovery journey data found
            return None

        userImageDetails = UserImageData()
        userImageDetails.fromJSON(userImageDataJSON)

        return userImageDetails    

    def activateMoov (self, moovId, userId, counterpartId, userContext: UserContextData):
        db = self.getDatabase();
        activeMoovsCollection = db["activeMoovs"]

        moovData = self.getMoov(moovId, userContext=userContext)

        #Check if there is an already moovId with userId and teamMember Id that is active
        existingMoov = self.getActiveMoovByMoovUserAndCounterpart(userId=userId, moovId=moovId, counterpartId=counterpartId)

        if existingMoov is not None:
            #rasie error active Moov already exists
            return existingMoov

        newActiveMoov = ActiveMoov()
        newActiveMoov.id = "AM_" + str(self.getNextCount())
        newActiveMoov.moovId = moovId
        newActiveMoov.userId = userId
        newActiveMoov.counterpartId = counterpartId
        newActiveMoov.issueId = moovData.issueId
        newActiveMoov.startDate = datetime.datetime.now()
        
        activeMoovsCollection.insert_one(newActiveMoov.toJSON())

        return newActiveMoov

    def getActiveMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "counterpartId": counterpartId}

        activeMoovsDataJSONList = activeMoovsCollection.find(activeMoovFilter)

        if (activeMoovsDataJSONList is None):
            return None

        foundActiveMoovs = []
        for currActiveMoovJSONData in activeMoovsDataJSONList:
            foundAcvtiveMoov = ExtendedActiveMoov()
            foundAcvtiveMoov.buildFromJSON(currActiveMoovJSONData)
            foundAcvtiveMoov.moovData = self.getMoov(foundAcvtiveMoov.moovId, userContext)
            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getActiveMoovsForUser (self, userId, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId": userId}

        activeMoovsDataJSONList = activeMoovsCollection.find(activeMoovFilter)

        if (activeMoovsDataJSONList is None):
            return None

        foundActiveMoovs = []
        for currActiveMoovJSONData in activeMoovsDataJSONList:
            foundAcvtiveMoov = ExtendedActiveMoov()
            foundAcvtiveMoov.buildFromJSON(currActiveMoovJSONData)
            foundAcvtiveMoov.moovData = self.getMoov(foundAcvtiveMoov.moovId, userContext)
            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "moovId":moovId,"counterpartId": counterpartId}

        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter)

        if (activeMoovJSONData is None):
            return None

        foundActiveMoov = ActiveMoov()
        foundActiveMoov.buildFromJSON(activeMoovJSONData)
   
        return foundActiveMoov

    def endMoov (self, activeMoovId, feedbackScore, feedbackText):
        db = self.getDatabase();
        activeMoovsCollection = db["activeMoovs"]
        historicMoovsCollections=db["historicMoovs"]

        activeMoovFilter = {"id":activeMoovId}
        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter) 
        
        if (activeMoovJSONData is not None):
            activeMoovDetails = ActiveMoov()
            activeMoovDetails.buildFromJSON(activeMoovJSONData)

            activeMoovDetails.endDate = datetime.datetime.now()
            activeMoovDetails.feedbackScore = feedbackScore
            activeMoovDetails.feedbackText = feedbackText

            # create a record in the historic data and delete from active moovs
            historicMoovsCollections.insert_one(activeMoovDetails.toJSON())
            activeMoovsCollection.delete_one(activeMoovFilter)