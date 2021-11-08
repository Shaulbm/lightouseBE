from threading import current_thread
from typing import Text
from pymongo import MongoClient
from pymongo.common import partition_node
from motivationsData import MotivationData, MotivationPartialData
from generalData import UserData, UserPartialData, UserRoles, UserCircleData, Gender, Locale
from questionsData import QuestionData
from singleton import Singleton
from discoveryData import UserDiscoveryJourneyData, DiscoveryBatchData
from loguru import logger
import anytree
from anytree import Node
from issuesData import IssueData, SubjectData

LOCALE_HEB_MA = 1
LOCALE_HEB_FE = 2
LOCALE_EN = 3


class moovDBInstance(metaclass=Singleton):
    def __init__(self):
        self.dataBaseInstance = None
        
    def getDatabase(self):

        if (self.dataBaseInstance is None):
            connectionString = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
            client = MongoClient(connectionString)
            self.dataBaseInstance = client.moov

        return self.dataBaseInstance

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

    def getMotivation (self, id, locale):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        motivationDataJSON = motivationCollection.find_one({"id" : id})

        if (motivationDataJSON is None):
            return None

        # print ("motivation data is {0}", motivationDataJSON)

        motivationTextsDic = self.getTextDataByParent(id, locale)

        newMotivtion = MotivationData()
        newMotivtion.buildFromJSON(motivationDataJSON, motivationTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return newMotivtion 
    
    def getAllMotivations(self,locale):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        motivationsDataJSONList = motivationCollection.find()

        if (motivationsDataJSONList is None):
            return None

        foundMotivations = []
        for currMotivationJSONData in motivationsDataJSONList:
            motivationTextsDic = self.getTextDataByParent(currMotivationJSONData["id"], locale)
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

    def getQuestion(self, id, locale=0):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        questionsDataJSON = questionsCollection.find_one({"id" : id})

        if (questionsDataJSON is None):
            return None

        questionTextsDic = None
        
        if (locale != Locale.UNKNOWN):
            # get id's for text quesry
            parentsIds = ([p["id"] for p in questionsDataJSON["possibleResponses"]])
            parentsIds.append(questionsDataJSON["id"])
            
            # get localed text
            questionTextsDic = self.getTextDataByParents(parentsIds, locale)

        questionDetails = QuestionData()
        questionDetails.buildFromJSON(questionsDataJSON, questionTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return questionDetails

    def getQuestionsFromBatch(self, batchId, locale):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        questionsDataJSON = questionsCollection.find({"batchId" : batchId})

        if (questionsDataJSON is None):
            return None        

        questionsInBatch = []

        for currQuestion in questionsDataJSON:
            questionsInBatch.append (self.getQuestion(currQuestion["id"], locale))

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

    def getDiscvoeryBatch(self, batchId = "", journeyId = "", batchIdx = "", locale = 0):
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

        localedTextDict = self.getTextDataByParent(discoveryBatchDataJSON["batchId"], locale)

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

    def getIssue(self, id, locale=Locale.UNKNOWN):
        db = self.getDatabase()
        issuesCollection = db["issues"]

        issueDataJSON = issuesCollection.find_one({"id" : id})

        if (issueDataJSON is None):
            return None

        issuesTextsDic = None
        
        if (locale != Locale.UNKNOWN):
            # get id's for text quesry
            parentsIds = []
            parentsIds.append(issueDataJSON["id"])
            parentsIds = parentsIds + ([p["id"] for p in issueDataJSON["contributingMotivations"]])
            parentsIds = parentsIds + ([p["id"] for p in issueDataJSON["resolvingMotivations"]]) 
            

            # get localed text
            issuesTextsDic = self.getTextDataByParents(parentsIds, locale)

        issueDetails = IssueData()
        issueDetails.buildFromJSON(jsonData = issueDataJSON, localedTextDic=issuesTextsDic)

        return issueDetails

    def getIssueForUser(self, id, userId, locale=Locale.UNKNOWN):

        issueDetails = self.getIssue (id=id, locale=Locale)
        userDetails = self.getUser(id=userId)

        # filter all the resolving motivations that are in the user motivations
        filteredResolvingMotivatios = [rm for rm in issueDetails.resolvingMotivations if rm.motivationId in userDetails.motivations]
        filteredContributingMotivatios = [cm for cm in issueDetails.contributingMotivations if cm.motivationId in userDetails.motivations]

        issueDetails.resolvingMotivations = filteredResolvingMotivatios.copy()
        issueDetails.contributingMotivations = filteredContributingMotivatios.copy()

        return issueDetails

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

    def getUserCircle(self, userId):
        db = self.getDatabase()

        userCircleDetails = UserCircleData()
        userCircleDetails.teamMembersList = self.getUsersUnder(userId)
        userCircleDetails.peopleOfInterest = self.getUserPeopleOfInterest(userId)

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
                    foundSubordinatesDataList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, gender=currentUserDetails.gender, orgId=currentUserDetails.orgId, motivations=currentUserDetails.motivations))

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
                    foundSubordinatesDataList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, gender=currentUserDetails.gender, orgId=currentUserDetails.orgId, motivations=currentUserDetails.motivations))

        return foundSubordinatesDataList

    def getUserPeopleOfInterest(self, userId):
        peopleOfInterestList = []

        requestingUser = self.getUser(id=userId)
        poiIdList = requestingUser.personsOfInterest 

        for currPOI in poiIdList:
            currentUserDetails = self.getUser(id=currPOI)
            peopleOfInterestList.append (UserPartialData(id = currentUserDetails.id, firstName = currentUserDetails.firstName, familyName=currentUserDetails.familyName, orgId=currentUserDetails.orgId, motivations=currentUserDetails.motivations))

        return peopleOfInterestList
