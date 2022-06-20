from ast import Not
from hashlib import new
from re import LOCALE
import threading
from tkinter import W
from wave import Wave_write
from pymongo import MongoClient
from pymongo.common import partition_node
from environmentProvider import EnvKeys
import environmentProvider as ep
from generalData import TrialData
from questionsData import QuestionsType
from moovData import IssueMoovData, ConflictMoovData, ExtendedConflictMoovData, MoovInstance, ExtendedMoovInstance, BaseMoovData
from motivationsData import MotivationData, MotivationPartialData, InsightTypeData, InsightsUserType, MotivationInsightData
from generalData import UserData, UserPartialData, UserRoles, Gender, Locale, UserContextData, UserCredData, UserRelationshipData
from questionsData import QuestionData
from singleton import Singleton
from discoveryData import UserDiscoveryJourneyData, DiscoveryBatchData
from loguru import logger
import anytree
from anytree import Node
from issuesData import IssueData, SubjectData, IssuePartialData, IssueExtendedData, ConflictData, ExtendedConflictData
import datetime
import logging

ROOT_USER_IMAGES_PATH = 'C:\\Dev\\Data\\UserImages'
DEFAULT_USER_IMAGES_DIR = 'Default'

class MoovDBInstance(metaclass=Singleton):
    def __init__(self):
        self.dataBaseInstance = None
        self.counterLock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def lock(self):
        self.counterLock.acquire()

    def release(self):
        self.counterLock.release()

    def getDatabase(self):

        if (self.dataBaseInstance is None):
            connectionString = "mongodb://localhost:27017/?readPreference=primary&appname=moovDB%20Compass&directConnection=true&ssl=false"
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

    def getTextDataByParent (self, parentId, locale, gender=Gender.MALE, name=""):
        textDataCollection = self.getTextCollectionByLocale(locale, gender)
            
        allTextsArray = textDataCollection.find ({"parentId" : parentId})

        textDic = {}

        for currText in allTextsArray:
            # if name is not empty, replace <<NAME>> or <<>> with the given name value
            if (name != ""):
                tempText = currText["text"].replace("<<NAME>>", name)
                tempText = tempText.replace("<<>>", name)
                tempText = tempText.replace("<< >>", name)
                textDic[currText["id"]] = tempText
            else:
                textDic[currText["id"]] = currText["text"]

        return textDic

    def getTextDataByParents (self, parentsIds, locale, gender=Gender.MALE, name=""):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale, gender, name)

        return resultTextDict


    def getTextCollectionByLocale(self, locale, gender):
        db = self.getDatabase()

        if locale == Locale.LOCALE_HE_IL:
            if gender == Gender.FEMALE:
                return db["locale_he_fe"]
            elif gender == Gender.MALE:
                return db["locale_he_ma"]
        elif locale == Locale.LOCALE_EN_US:
            return db["locale_en"]
        
        #default
        return db ["locale_en"]

    def getMGTextDataByParent(self, parentId, locale, firstGender, secondGender, name=""):
        textDataCollection = self.getMGTextCollectionByLocale(locale=locale, firstGender=firstGender, secondGender=secondGender)
            
        allTextsArray = textDataCollection.find ({"parentId" : parentId})

        textDic = {}

        for currText in allTextsArray:
            # if name is not empty, replace <<NAME>> or <<>> with the given name value
            if (name != ""):
                tempText = currText["text"].replace("<<NAME>>", name)
                tempText = tempText.replace("<<>>", name)
                tempText = tempText.replace("<< >>", name)
                textDic[currText["id"]] = tempText
            else:
                textDic[currText["id"]] = currText["text"]

        return textDic

    def geMGtTextDataByParents (self, parentsIds, locale, firstGender, secondGender, name=""):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale, firstGender, secondGender, name)

        return resultTextDict

    #multi gender locale support 
    def getMGTextCollectionByLocale(self, locale, firstGender, secondGender):
        db = self.getDatabase()

        if locale == Locale.LOCALE_HE_IL:
            if firstGender == Gender.FEMALE:
                if secondGender == Gender.FEMALE:
                    return db["locale_mg_he_fe_fe"]
                elif secondGender == Gender.MALE:
                    return db["locale_mg_he_fe_ma"]
            elif firstGender == Gender.MALE:
                if secondGender == Gender.FEMALE:
                    return db["locale_mg_he_ma_fe"]
                elif secondGender == Gender.MALE:
                    return db["locale_mg_he_ma_ma"]
        elif locale == Locale.LOCALE_EN_US:
            if secondGender == Gender.FEMALE:
                return db["locale_mg_en_fe"]
            elif secondGender == Gender.MALE:
                return db["locale_mg_en_ma"]
        
        #default
        return db ["locale_mg_en_ma"]

    def insertOrUpdateMotivation (self, motivationDetails):
        db = self.getDatabase()
        motivationsCollection = db["motivations"]
        motivationDataJSON = motivationsCollection.find_one({"id" : motivationDetails.id})

        if (motivationDataJSON is not None):
            #object found
            motivationFilter = {'id':motivationDetails.id}
            motivationsCollection.replace_one (motivationFilter, motivationDetails.toJSON())
        else:
            # this is a new motivation
            motivationsCollection.insert_one(motivationDetails.toJSON())

    def insertOrUpdateMotivationInsight (self, insightDetails):
        db = self.getDatabase()
        insightsCollection = db["motivationsInsights"]
        insightDataJSON = insightsCollection.find_one({"id" : insightDetails.id})

        if (insightDataJSON is not None):
            #object found
            insightFilter = {'id':insightDetails.id}
            insightsCollection.replace_one (insightFilter, insightDetails.toJSON())
        else:
            # this is a new insight
            insightsCollection.insert_one(insightDetails.toJSON())

    def insertOrUpdateInsightType (self, insightTypeDetails):
        db = self.getDatabase()
        insightsTypesCollection = db["motivationsInsightsTypes"]
        insightTypeDataJSON = insightsTypesCollection.find_one({"id" : insightTypeDetails.id})

        if (insightTypeDataJSON is not None):
            #object found
            insightFilter = {'id':insightTypeDetails.id}
            insightsTypesCollection.replace_one (insightFilter, insightTypeDetails.toJSON())
        else:
            # this is a new insight
            insightsTypesCollection.insert_one(insightTypeDetails.toJSON())

    def getInsightsForCounterpart (self, counterpartDetails, userContext : UserContextData):
        db = self.getDatabase()
        insightsCollection = db["motivationsInsights"]

        if (counterpartDetails.motivations is None or counterpartDetails.motivations.__len__ == 0):
            return {}

        counterpartMotivationsIds = list(counterpartDetails.motivations.keys())

        insightsFilter = {"type":InsightsUserType.TEAM_MEMBER,"motivationId": {"$in":counterpartMotivationsIds}}
        insightsDataJSONList = insightsCollection.find(insightsFilter)

        if (insightsDataJSONList is None):
            return None

        foundInsights = []
        for currInsightJSONData in insightsDataJSONList:
            insightTextsDic = self.getTextDataByParent(parentId= currInsightJSONData["id"], locale= userContext.locale, gender = counterpartDetails.gender, name= counterpartDetails.firstName)            
            newInisight = MotivationInsightData()
            newInisight.buildFromJSON(currInsightJSONData, insightTextsDic)
            foundInsights.append(newInisight)

        return foundInsights        

    def getInsightsForSelf (self, userDetails : UserData, userContext : UserContextData):
        db = self.getDatabase()
        insightsCollection = db["motivationsInsights"]

        if (userDetails.motivations is None or userDetails.motivations.__len__ == 0):
            return {}

        userMotivationsIds = list(userDetails.motivations.keys())

        insightsType = InsightsUserType.SELF_MANAGER

        if userDetails.role == UserRoles.EMPLOYEE:
            insightsType = InsightsUserType.SELF_EMPLOYEE

        insightsFilter = {"type":insightsType,"motivationId": {"$in":userMotivationsIds}}
        insightsDataJSONList = insightsCollection.find(insightsFilter)

        if (insightsDataJSONList is None):
            return None

        foundInsights = []
        for currInsightJSONData in insightsDataJSONList:
            insightTextsDic = self.getTextDataByParent(parentId= currInsightJSONData["id"], locale= userContext.locale, gender = userDetails.gender, name= userDetails.firstName)            
            newInisight = MotivationInsightData()
            newInisight.buildFromJSON(currInsightJSONData, insightTextsDic)
            foundInsights.append(newInisight)

        return foundInsights      

    def getInsightsTypes (self, targetUser : InsightsUserType, userContext : UserContextData, counterpartDetails = None):
        db = self.getDatabase()
        insightsTypesCollection = db["motivationsInsightsTypes"]

        insightsFilter = {"type":targetUser}
        insightsDataJSONList = insightsTypesCollection.find(insightsFilter)

        if (insightsDataJSONList is None):
            return None

        counterpartName = ""
        counterpartGender = Gender.MALE
        if (counterpartDetails is not None):
            counterpartName = counterpartDetails.firstName
            counterpartGender = counterpartDetails.gender

        foundInsightsTypes = []
        for currInsightTypeJSONData in insightsDataJSONList:
            insightTypeTextsDic = self.getTextDataByParent(parentId= currInsightTypeJSONData["id"], locale= userContext.locale, name=counterpartName, gender= counterpartGender)            
            newInsightType = InsightTypeData()
            newInsightType.buildFromJSON(currInsightTypeJSONData, insightTypeTextsDic)
            foundInsightsTypes.append(newInsightType)

        return foundInsightsTypes   

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

    def insertOrUpdateConflictMoov (self, moovDataObj):
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

    def getConflictMoovs (self, conflictId, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        moovsDataJSON = moovsCollection.find({"conflictId" : conflictId})
        ConflictDetails = self.getConflict(conflictId, userContext)

        if (moovsDataJSON is None):
            return None

        moovTextsDic = None

        foundMoovs = []
        for currMoovJSONData in moovsDataJSON:
            moovTextsDic = self.getTextDataByParent(currMoovJSONData["id"], userContext.locale, userContext.gender)
            newMoov = ExtendedConflictMoovData()
            newMoov.buildFromJSON(currMoovJSONData, moovTextsDic)
            newMoov.conflictScore = ConflictDetails.score
            foundMoovs.append(newMoov)

        return foundMoovs

    def getConflictsMoovsForUsers (self, teamMemberId, counterpartId, userContext: UserContextData):
        conflictsList = self.getConflictsForUsers(teamMemberId=teamMemberId, counterpartId=counterpartId, partialData=  True, userContext=userContext)

        conflictsMoovs = []

        for currConflict in conflictsList:
            currConflictMoovs = self.getConflictMoovs(conflictId=currConflict.id, userContext=userContext)

            conflictsMoovs = conflictsMoovs + currConflictMoovs

        return conflictsMoovs

    def getIssueMoov (self, id, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        moovDataJSON = moovsCollection.find_one({"id" : id})

        if (moovDataJSON is None):
            return None

        moovTextsDic = None
        if (userContext is not None):
            # In this context gender is not an issue 
            moovTextsDic = self.getMGTextDataByParent(id, Gender.MALE, Gender.MALE, userContext.locale)

        newMoov = IssueMoovData()
        newMoov.buildFromJSON(moovDataJSON, moovTextsDic)

        return newMoov 

    def getBaseMoov (self, id, counterpartDetails, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        moovDataJSON = moovsCollection.find_one({"id" : id})

        if (moovDataJSON is None):
            return None

        moovTextsDic = None
        if (userContext is not None):
            moovTextsDic = self.getMGTextDataByParent(parentId=id, locale=userContext.locale, firstGender=userContext.gender, secondGender=counterpartDetails.gender, name=counterpartDetails.firstName)

        foundMoov = BaseMoovData()
        foundMoov.buildFromJSON(moovDataJSON, moovTextsDic)

        return foundMoov 

    def getMoovsForIssueAndCounterpart (self, counterpartDetails, issueId, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        if (counterpartDetails.motivations is None or counterpartDetails.motivations.__len__ == 0):
            return {}

        userMotivationsIds = list(counterpartDetails.motivations.keys())

        moovFilter = {"issueId":issueId,"motivationId": {"$in":userMotivationsIds}}
        motivationsDataJSONList = moovsCollection.find(moovFilter)

        if (motivationsDataJSONList is None):
            return None

        foundMoovs = []
        for currMoovJSONData in motivationsDataJSONList:
            moovTextsDic = None

            if (userContext is not None):
                moovTextsDic = self.getMGTextDataByParent(parentId= currMoovJSONData["id"], locale= userContext.locale, firstGender= userContext.gender, secondGender= counterpartDetails.gender, name= counterpartDetails.firstName)            
            
            newMoov = IssueMoovData()
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
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=locale, gender=gender, orgId=orgId, role=role, mailAddress=mailAddress, motivations=motivations, personsOfInterest=personsOfInterest)
        self.insertOrUpdateUser(newUser)

    def insertOrUpdateUser (self, currUserData):
        db = self.getDatabase()
        usersCollection = db["users"]

        # set isRTL by the provided Locale
        if (currUserData.locale == Locale.LOCALE_HE_IL):
            currUserData.isRTL = True
        else:
            currUserData.isRTL = False

        foundUser = usersCollection.find_one({"id":currUserData.id})

        currUserData.mailAddress = currUserData.mailAddress.lower()

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

        motivationTextsDic = self.getTextDataByParent(id, userContext.locale, userContext.gender)

        foundMotivation = MotivationData()
        foundMotivation.buildFromJSON(motivationDataJSON, motivationTextsDic)

        return foundMotivation 

    def getAllMotivations(self,userContext:UserContextData):
        db = self.getDatabase()
        motivationCollection = db["motivations"]

        motivationsDataJSONList = motivationCollection.find()

        if (motivationsDataJSONList is None):
            return None

        foundMotivations = []
        for currMotivationJSONData in motivationsDataJSONList:
            motivationTextsDic = self.getTextDataByParent(currMotivationJSONData["id"], userContext.locale, userContext.gender)
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
            motivationTextsDic = self.getTextDataByParent(currMotivationJSONData["id"], userContext.locale, userContext.gender)
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

    def getUserPassword (self, userId):
        db = self.getDatabase()
        usersCollection = db["usersCreds"]

        userFilter = {"id":userId}
        userCredDataJSON = usersCollection.find_one(userFilter)

        if (userCredDataJSON is None):
            #no user found
            return ""

        if ("password" not in userCredDataJSON):
            return ""

        userCredDetails = UserCredData()
        userCredDetails.fromJSON(userCredDataJSON)
        return userCredDetails.password

    def setUserPassword (self, userCreds: UserCredData):
        db = self.getDatabase()
        usersCredCollection = db["usersCreds"]

        foundUserCred = usersCredCollection.find_one({"id":userCreds.id})

        if (foundUserCred is not None):
            #the user creds already exists - update
            userDataFilter = {"id" : userCreds.id}
            usersCredCollection.replace_one(userDataFilter, userCreds.toJSON())
        else:
            #this is a new user cred
            usersCredCollection.insert_one(userCreds.toJSON())

    def getUser (self, id):
        db = self.getDatabase()
        usersCollection = db["users"]

        userFilter = {"id":id}

        userDataJSON = usersCollection.find_one(userFilter)

        if (userDataJSON is None):
            #no user found
            return None

        userDetails = UserData()
        userDetails.fromJSON(userDataJSON)

        return userDetails

    def getAllUsers(self):
        db = self.getDatabase()
        usersCollection = db["users"]

        userDataJSONList = usersCollection.find()

        if (userDataJSONList is None):
            #no users found
            return None

        usersList = []

        for currUserJSONData in userDataJSONList:
            foundUser = UserData()
            foundUser.fromJSON(currUserJSONData)
            usersList.append(foundUser)        

        return usersList

    def getUserByMail (self, mail):
        db = self.getDatabase()
        usersCollection = db["users"]

        userFilter = {"mailAddress":mail.lower()}

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
        
        # print ('in getQuestion user Context is ', userContext.toJSON())

        if (userContext is not None and userContext.locale != Locale.UNKNOWN):
            # get id's for text quesry
            parentsIds = ([p["id"] for p in questionsDataJSON["possibleResponses"]])
            parentsIds.append(questionsDataJSON["id"])
            
            # get localed text
            questionTextsDic = self.getTextDataByParents(parentsIds, userContext.locale, userContext.gender)

        questionDetails = QuestionData()
        print ('in MoovDB:getQuestion question id is', questionsDataJSON['id'])

        if questionTextsDic is not None and questionTextsDic.__len__ == 0:
            questionTextsDic = None

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

    def getMotivationGapQuestionsByMotivationsIds(self, motivationsIdsList, userContext : UserContextData):
        db = self.getDatabase()
        questionsCollection = db["questions"]

        questionsFilter = {'motivationId': {'$in': motivationsIdsList}, 'type' : QuestionsType.MOTIVATION_GAP}

        foundQuestions = questionsCollection.find(questionsFilter)

        questionsList = []
        for foundQuestion in foundQuestions:

            questionTextsDic = None
            if (userContext.locale != Locale.UNKNOWN):
                # get id's for text quesry
                parentsIds = ([p["id"] for p in foundQuestion["possibleResponses"]])
                parentsIds.append(foundQuestion["id"])

                # get localed text
                questionTextsDic = self.getTextDataByParents(parentsIds, userContext.locale, userContext.gender)

            currQuestionDetails = QuestionData()
            currQuestionDetails.buildFromJSON(foundQuestion, questionTextsDic)

            questionsList.append(currQuestionDetails)

        return questionsList

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

        localedTextDict = self.getTextDataByParent(discoveryBatchDataJSON["batchId"], userContext.locale, userContext.gender)

        discoveryBatchDetails = DiscoveryBatchData()
        discoveryBatchDetails.buildFromJSON(discoveryBatchDataJSON, localedTextDict)

        return discoveryBatchDetails   

    def insertOrUpdateIssue(self, currIssueData):
        db = self.getDatabase()
        issuesCollection = db["issues"]

        foundIssue = issuesCollection.find_one({"id":currIssueData.id})

        if (foundIssue is not None):
            #the issue already exists - update the issue
            issueDataFilter = {"id" : currIssueData.id}
            issuesCollection.replace_one(issueDataFilter, currIssueData.toJSON())
        else:
            #this is a new issue
            issuesCollection.insert_one(currIssueData.toJSON())

    def insertOrUpdateTrial(self, trialDetails):
        db = self.getDatabase()
        trialsCollection = db["trials"]

        foundTrial = trialsCollection.find_one({"id": trialDetails.id})

        if (foundTrial is not None):
            # the trial already exists in the DB - update the trial data
            trialDataFilter = {"id": trialDetails.id}
            trialsCollection.replace_one(trialDataFilter, trialDetails.toJSON())
        else:
            # this is a new trial
            trialsCollection.insert_one(trialDetails.toJSON())

    def getIssueByDetails (self, id, locale, gender, name):
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
            issuesTextsDic = self.getTextDataByParents(parentsIds, locale, gender, name=name )

        issueDetails = IssueData()
        issueDetails.buildFromJSON(jsonData = issueDataJSON, localedTextDic=issuesTextsDic)

        return issueDetails

    def getIssue(self, id, userContext: UserContextData, name = ""):
        if (userContext is None):
            return self.getIssueByDetails(id=id, locale=Locale.UNKNOWN, gender = Gender.MALE, name = name)
        else:
            return self.getIssueByDetails(id=id, locale=userContext.locale, gender = userContext.gender, name = name)


    def insertOrUpdateConflict(self, currConflictData):
        db = self.getDatabase()
        conflictsCollection = db["conflicts"]

        foundConflict = conflictsCollection.find_one({"id":currConflictData.id})

        if (foundConflict is not None):
            #the conflict already exists - update the issue
            conflictDataFilter = {"id" : currConflictData.id}
            conflictsCollection.replace_one(conflictDataFilter, currConflictData.toJSON())
        else:
            #this is a new conflict
            conflictsCollection.insert_one(currConflictData.toJSON())

    def getConflict(self, id, userContext: UserContextData):
        db = self.getDatabase()
        conflictsCollection = db["conflicts"]

        conflictDataJSON = conflictsCollection.find_one({"id" : id})

        if (conflictDataJSON is None):
            return None

        conflictssTextsDic = None
        
        if (userContext is not None):
            # get id's for text quesry
            parentsIds = []
            parentsIds.append(conflictDataJSON["id"])            

            # get localed text
            conflictssTextsDic = self.getTextDataByParents(parentsIds, userContext.locale, userContext.gender)

        conflictDetails = ConflictData()
        conflictDetails.buildFromJSON(jsonData = conflictDataJSON, localedTextDic=conflictssTextsDic)

        return conflictDetails

    def getConflictsForUsers (self, teamMemberId, counterpartId, partialData: bool, userContext : UserContextData):
        teamMemberMotivations = self.getUserMotivations(teamMemberId, userContext)
        counterpartMotivations = self.getUserMotivations(counterpartId, userContext)

        if (teamMemberMotivations.__len__() == 0 or counterpartMotivations.__len__ == 0):
            return None
        
        teamMemberMotivationIds = []
        counterpartMotivationsIds = []

        teamMemberMotivationIds = [m.id for m in teamMemberMotivations]
        counterpartMotivationsIds = [m.id for m in counterpartMotivations]
        

        conflictFilter = {'$or':[{'motivationId': {'$in': teamMemberMotivationIds}, 'motivationCounterpartId': {'$in': counterpartMotivationsIds}}, {'motivationId': {'$in': counterpartMotivationsIds}, 'motivationCounterpartId': {'$in': teamMemberMotivationIds}}]}

        print ('filter is ', str(conflictFilter))

        db = self.getDatabase()
        conflictsCollection = db["conflicts"]

        foundConflicts = conflictsCollection.find(conflictFilter)

        conflictsDetails = []

        # create a joint list of the motivations - this is for use in the loop
        jointMotivatios = []
        counterpartMotivationsIds 
        for currMotivation in teamMemberMotivations:
            if currMotivation.id not in counterpartMotivationsIds:
                jointMotivatios.append(currMotivation)

        jointMotivatios = jointMotivatios + counterpartMotivations

        for currFoundConflictJSON in foundConflicts:
            conflictTextsDic = self.getTextDataByParent(currFoundConflictJSON["id"], userContext.locale, userContext.gender)
            
            currConflictDetails = ExtendedConflictData()
            currConflictDetails.buildFromJSON(currFoundConflictJSON, conflictTextsDic)

            if not partialData:
                userMotivation = next((m for m in jointMotivatios if m.id == currConflictDetails.motivationId), None)
                counterpartMotivation = next((m for m in jointMotivatios if m.id == currConflictDetails.motivationCounterpartId), None)
                
                if (userMotivation is not None and counterpartMotivation is not None):
                    currConflictDetails.motivationName = userMotivation.name
                    currConflictDetails.motivationCounterpartName = counterpartMotivation.name

            conflictsDetails.append(currConflictDetails)

        return conflictsDetails

    def getIssuesForSubject (self, subjectId, userContext: UserContextData):
        db = self.getDatabase()
        subjectsCollection = db["issues"]

        dataFilter = {"subjectId": subjectId}

        issuesDataJSONList = subjectsCollection.find(dataFilter)

        issuesDetailsList = []

        for currIssueJSONData in issuesDataJSONList:
            issueTextsDic = self.getTextDataByParent(currIssueJSONData["id"], userContext.locale, userContext.gender)
            newIssue = IssuePartialData()
            newIssue.buildFromJSON(currIssueJSONData, issueTextsDic)
            issuesDetailsList.append(newIssue)        

        return issuesDetailsList
    
    def getAllIssues (self, issuesGender, userContext: UserContextData, counterpartName = ""):
        db = self.getDatabase()
        subjectsCollection = db["issues"]

        issuesDataJSONList = subjectsCollection.find()

        issuesDetailsList = []

        for currIssueJSONData in issuesDataJSONList:
            issueTextsDic = self.getTextDataByParent(currIssueJSONData["id"], userContext.locale, issuesGender, name = counterpartName)
            newIssue = IssuePartialData()
            newIssue.buildFromJSON(currIssueJSONData, issueTextsDic)
            issuesDetailsList.append(newIssue)        

        return issuesDetailsList
    
    def getIssueForCounterpart(self, issueId, counterpartId, userContext: UserContextData):
        counterpartDetails = self.getUser(id=counterpartId)
        issueDetails = self.getIssueByDetails (id=issueId, locale=userContext.locale, gender=counterpartDetails.gender, name=counterpartDetails.firstName)

        # filter all the resolving motivations that are in the counterpart motivations
        filteredResolvingMotivatios = [rm for rm in issueDetails.resolvingMotivations if rm.motivationId in counterpartDetails.motivations]
        filteredContributingMotivatios = [cm for cm in issueDetails.contributingMotivations if cm.motivationId in counterpartDetails.motivations]

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
            subjectTextsDic = self.getTextDataByParent(currSubjectJSONData["id"], userContext.locale, userContext.gender)
            newSubject = SubjectData()
            newSubject.buildFromJSON(currSubjectJSONData, subjectTextsDic)
            foundSubjects.append(newSubject)

        return foundSubjects

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
                    userPartialDetails = UserPartialData()
                    userPartialDetails.fromFullDetails(currentUserDetails)
                    userPartialDetails.activeMoovsCount = self.getActiveMoovsCountToCounterpart(userId=userId, counterpartId=userPartialDetails.id)
                    foundSubordinatesDataList.append (userPartialDetails)

            return foundSubordinatesDataList

        # the requesting user is not the HR, find all the users under this user
        rootNode = Node('root')
        requestingUserNode = None

        # for each user in the organization
        for currentFoundUser in foundUsers:
            currentUserDetails = UserData()
            currentUserDetails.fromJSON(currentFoundUser)
            
            currentUserNode = anytree.search.find_by_attr(rootNode, currentUserDetails.id)

            currentUserParentNode = rootNode
            if (currentUserDetails.parentId != ""):
                currentUserParentNode = anytree.search.find_by_attr(rootNode, currentUserDetails.parentId)

            if (currentUserParentNode is None):
                #this is the first time we find this Id
                currentUserParentNode = Node(currentUserDetails.parentId, rootNode)
            
            if (currentUserNode is None):
                #this is the first time we find this Id
                currentUserNode = Node (currentUserDetails.id, currentUserParentNode)
            else:
                # this user Id is already in the tree - set it under the right parent
                currentUserNode.parent = currentUserParentNode

            if (currentUserDetails.id == userId):
                #this is the user that we want to get all his subordinates
                requestingUserNode = currentUserNode

        foundSubordinates = None

        if requestingUser.presentFullHierarchy:
            # now we have the organization hierarchy, get the list of all this managers subordinates
            foundSubordinates = anytree.search.findall(requestingUserNode)
        else:    
            # find all the users that are directly under
            foundSubordinates = requestingUserNode.children

        if (foundSubordinates is not None):
            foundSubordinatesList = list(foundSubordinates)
            for currentSubordinate in foundSubordinatesList:
                if (currentSubordinate.name != requestingUser.id):
                    #the manager is also part of the nodes list and should be ignored
                    userPartialDetails = UserPartialData()
                    userPartialDetails.fromFullDetails(self.getUser(currentSubordinate.name))
                    userPartialDetails.activeMoovsCount = self.getActiveMoovsCountToCounterpart(userId=userId, counterpartId=userPartialDetails.id)
                    foundSubordinatesDataList.append (userPartialDetails)

        return foundSubordinatesDataList

    def getUsersInOrg (self, orgId):
        if (orgId is None or orgId == ""):
            return None

        foundSubordinatesDataList = []

        db = self.getDatabase()
        usersCollection = db["users"]

        # get all users in the user organization
        foundUsers = usersCollection.find({"orgId":orgId})

        if (foundUsers is None):
            # no users in the organization
            return foundSubordinatesDataList

        for currentFoundUser in foundUsers:
            currentUserDetails = UserData()
            currentUserDetails.fromJSON(currentFoundUser)
            foundSubordinatesDataList.append (currentUserDetails)

        return foundSubordinatesDataList

    #return the users that the given UserId is in their POI
    def getInterestedUsers(self, userId):
        db = self.getDatabase()
        usersCollection = db["users"]

        usersFillter = {"personsOfInterest" : userId}
        foundUsersRaw = usersCollection.find(usersFillter)

        foundUsersDetails = []

        for currUserJSON in foundUsersRaw:
            currUserDetails = UserData()
            currUserDetails.fromJSON(currUserJSON)
            foundUsersDetails.append(currUserDetails)

        return foundUsersDetails

    def activateIssueMoov (self, moovId, userId, counterpartId, priority, userContext: UserContextData):
        db = self.getDatabase();
        activeMoovsCollection = db["activeMoovs"]

        #Check if there is an already moovId with userId and teamMember Id that is active
        existingMoov = self.getActiveMoovByMoovUserAndCounterpart(userId=userId, moovId=moovId, counterpartId=counterpartId)

        if existingMoov is not None:
            #rasie error active Moov already exists
            return existingMoov

        newActiveMoov = MoovInstance()
        newActiveMoov.id = "AM_" + str(self.getNextCount())
        newActiveMoov.moovId = moovId
        newActiveMoov.userId = userId
        newActiveMoov.counterpartId = counterpartId
        newActiveMoov.priority = priority
        newActiveMoov.startDate = datetime.datetime.utcnow()
        newActiveMoov.plannedEndDate = newActiveMoov.startDate + datetime.timedelta(days=ep.getAttribute(EnvKeys.behaviour, EnvKeys.daysToAccomplishActiveMoov))

        self.insertOrUpdateActiveMoov(newActiveMoov)        

        return newActiveMoov

    def insertOrUpdateActiveMoov (self, activeMoov : MoovInstance):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        foundActiveMoov = activeMoovsCollection.find_one({"id":activeMoov.id})

        if foundActiveMoov is not None:
            activeMoovDataFilter = {"id":activeMoov.id}
            activeMoovsCollection.replace_one(activeMoovDataFilter, activeMoov.toJSON())
        else:
            activeMoovsCollection.insert_one(activeMoov.toJSON())

    def getActiveMoov (self, id):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        foundActiveMoov = activeMoovsCollection.find_one({"id":id})

        activeMoovDetails = None
        if foundActiveMoov is not None:
            activeMoovDetails = MoovInstance()
            activeMoovDetails.buildFromJSON(foundActiveMoov)

        return activeMoovDetails

    def activateConflictMoov (self, moovId, userId, counterpartsIds, priority, userContext: UserContextData):
        # db = self.getDatabase()
        # activeMoovsCollection = db["activeMoovs"]

        # #Check if there is an already moovId with userId and teamMember Id that is active
        # existingMoov = self.getActiveMoovByMoovUserAndMultipleCounterparts(userId=userId, moovId=moovId, counterpartsIds=counterpartsIds)

        # if existingMoov is not None:
        #     #rasie error active Moov already exists
        #     return existingMoov

        # newActiveMoov = MoovInstance()
        # newActiveMoov.id = "AM_" + str(self.getNextCount())
        # newActiveMoov.moovId = moovId
        # newActiveMoov.userId = userId
        # newActiveMoov.counterpartsIds = counterpartsIds.copy()
        # newActiveMoov.priority = priority
        # newActiveMoov.startDate = datetime.datetime.utcnow()
        # newActiveMoov.plannedEndDate = newActiveMoov.startDate + datetime.timedelta(days=ep.getAttribute(EnvKeys.behaviour, EnvKeys.daysToAccomplishActiveMoov))
        
        # activeMoovsCollection.insert_one(newActiveMoov.toJSON())

        # return newActiveMoov
        pass

    def getActiveMoovsToCounterpart (self, userId, counterpartDetails:UserData, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "counterpartId": counterpartDetails.id}

        activeMoovsDataJSONList = activeMoovsCollection.find(activeMoovFilter)

        if (activeMoovsDataJSONList is None):
            return None

        foundActiveMoovs = []
        for currActiveMoovJSONData in activeMoovsDataJSONList:
            foundAcvtiveMoov = ExtendedMoovInstance()
            foundAcvtiveMoov.buildFromJSON(currActiveMoovJSONData)
            foundAcvtiveMoov.moovData = self.getBaseMoov(foundAcvtiveMoov.moovId, counterpartDetails = counterpartDetails, userContext=userContext)

            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getActiveMoovsCountToCounterpart (self, userId, counterpartId):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "counterpartId": counterpartId}

        activeMoovsCount = activeMoovsCollection.find(activeMoovFilter).count()

        return activeMoovsCount

    def getPastMoovsToCounterpart (self, userId, counterpartDetails, userContext: UserContextData):
        db = self.getDatabase()
        historicMoovsCollection = db["historicMoovs"]

        historicMoovFilter = {"userId":userId, "counterpartId": counterpartDetails.id}

        historicMoovsDataJSONList = historicMoovsCollection.find(historicMoovFilter)

        if (historicMoovsDataJSONList is None):
            return None

        foundHistoricMoovs = []
        for currHistoricMoovJSONData in historicMoovsDataJSONList:
            foundHistoricMoov = ExtendedMoovInstance()
            foundHistoricMoov.buildFromJSON(currHistoricMoovJSONData)
            foundHistoricMoov.moovData = self.getBaseMoov(foundHistoricMoov.moovId, counterpartDetails, userContext)
            foundHistoricMoovs.append(foundHistoricMoov)
   
        return foundHistoricMoovs

    def getPastMoovsToMoovAndCounterpart (self, userId, counterpartDetails, moovId, userContext: UserContextData):
        db = self.getDatabase()
        historicMoovsCollection = db["historicMoovs"]

        historicMoovFilter = {"userId":userId, "counterpartId": counterpartDetails.id, "moovId":moovId}

        historicMoovsDataJSONList = historicMoovsCollection.find(historicMoovFilter)

        if (historicMoovsDataJSONList is None):
            return None

        foundHistoricMoovs = []
        for currHistoricMoovJSONData in historicMoovsDataJSONList:
            foundHistoricMoov = ExtendedMoovInstance()
            foundHistoricMoov.buildFromJSON(currHistoricMoovJSONData)
            foundHistoricMoov.moovData = self.getBaseMoov(foundHistoricMoov.moovId, counterpartDetails, userContext)
            foundHistoricMoovs.append(foundHistoricMoov)
   
        return foundHistoricMoovs

    def getPartialActiveMoovsForUser (self, userId, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId": userId}

        activeMoovsDataJSONList = activeMoovsCollection.find(activeMoovFilter)

        if (activeMoovsDataJSONList is None):
            return None

        foundActiveMoovs = []
        for currActiveMoovJSONData in activeMoovsDataJSONList:
            foundAcvtiveMoov = ExtendedMoovInstance()
            foundAcvtiveMoov.buildFromJSON(currActiveMoovJSONData)
            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "moovId":moovId,"counterpartId": counterpartId}

        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter)

        if (activeMoovJSONData is None):
            return None

        foundActiveMoov = MoovInstance()
        foundActiveMoov.buildFromJSON(activeMoovJSONData)
   
        return foundActiveMoov

    def getActiveMoovByMoovUserAndMultipleCounterparts(self, userId, moovId, counterpartsIds):
        # db = self.getDatabase()
        # activeMoovsCollection = db["activeMoovs"]

        # activeMoovFilter = {"userId":userId, "moovId":moovId,"counterpartsIds": {"$all": counterpartsIds}}

        # activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter)

        # if (activeMoovJSONData is None):
        #     return None

        # foundActiveMoov = MoovInstance()
        # foundActiveMoov.buildFromJSON(activeMoovJSONData)
   
        # return foundActiveMoov
        pass

    def endMoov (self, activeMoovId, feedbackScore, feedbackText, isEndedByTimer):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]
        historicMoovsCollections=db["historicMoovs"]

        activeMoovFilter = {"id":activeMoovId}
        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter) 
        
        if (activeMoovJSONData is not None):
            activeMoovDetails = MoovInstance()
            activeMoovDetails.buildFromJSON(activeMoovJSONData)

            activeMoovDetails.endDate = datetime.datetime.now()
            activeMoovDetails.feedbackScore = feedbackScore
            activeMoovDetails.feedbackText = feedbackText

            # create a record in the historic data and delete from active moovs
            historicMoovsCollections.insert_one(activeMoovDetails.toJSON())
            activeMoovsCollection.delete_one(activeMoovFilter)

    def getAllMoovsPlannedToEnd(self, timeStamp, ignoreUserNotifications = False):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        # don't pick overdue moovs as they were handled
        if ignoreUserNotifications:
            activeMoovsFilter = {'plannedEndDate': {'$lt': timeStamp}, 'isOverdue': False}
        else:
            activeMoovsFilter = {'plannedEndDate': {'$lt': timeStamp}, 'notifiedUserForOverdue': False ,'isOverdue': False}
        foundMoovsData = activeMoovsCollection.find(activeMoovsFilter)

        activeMoovs = []
        for currMoovJSONData in foundMoovsData:
            currMoov = MoovInstance()
            currMoov.buildFromJSON(currMoovJSONData)
            activeMoovs.append(currMoov)

        return activeMoovs

    def updateMoovInstane(self, moovInstance):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        foundMoov = activeMoovsCollection.find_one({"id":moovInstance.id})

        if (foundMoov is not None):
            #the conflict already exists - update the issue
            moovsDataFilter = {"id" : moovInstance.id}
            activeMoovsCollection.replace_one(moovsDataFilter, moovInstance.toJSON())

    def insertOrUpdateRelationship (self, relationshipData):
        db = self.getDatabase()
        relationshipsCollection = db["relationships"]

        foundRelationship = relationshipsCollection.find_one({"userId":relationshipData.userId, "counterpartId":relationshipData.counterpartId})

        if (foundRelationship is not None):
            #the relationship already exists - update the relationship but also back up to history
            
            questionDataFilter = {"userId":relationshipData.userId, "counterpartId":relationshipData.counterpartId}
            relationshipsCollection.replace_one(questionDataFilter, relationshipData.toJSON())

            # remove the _id key so that Mongo will create a new id
            del (foundRelationship["_id"])

            historicRelationshipsCollection = db["historicRelationships"]
            historicRelationshipsCollection.insert_one(foundRelationship)

        else:
            #this is a new user
            relationshipsCollection.insert_one(relationshipData.toJSON())

    def getRelationshipData (self, userId, counterpartId):
        db = self.getDatabase()
        relationsheepsCollection = db["relationships"]

        foundRelationship = relationsheepsCollection.find_one({"userId":userId, "counterpartId":counterpartId})

        relationshipDetails = None

        if (foundRelationship is not None):
            relationshipDetails = UserRelationshipData()
            relationshipDetails.fromJSON(foundRelationship)

        return relationshipDetails

    def getTrialDetails(self, trialId):
        db = self.getDatabase()
        trialsCollection = db["trials"]

        foundTrial = trialsCollection.find_one({"id": trialId})

        trialDetails = None
        
        if (foundTrial is not None):
            trialDetails = TrialData()
            trialDetails.fromJSON(foundTrial)

        return trialDetails

    def getTrialDetailsByUser(self, userMail):
        db = self.getDatabase()
        trialsCollection = db["trials"]

        foundTrial = trialsCollection.find_one({"userMail": userMail})

        trialDetails = None
        
        if (foundTrial is not None):
            trialDetails = TrialData()
            trialDetails.fromJSON(foundTrial)

        return trialDetails

    