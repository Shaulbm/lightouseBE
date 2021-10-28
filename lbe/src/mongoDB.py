from threading import current_thread
from typing import Text
from google.auth import app_engine
from pymongo import MongoClient
import pymongo
import json
from motivationsData import motivationData
from generalData import TextData, UserData, UserRoles
from questionsData import QuestionData
from singleton import Singleton
from discoveryData import UserDiscoveryJourneyData, DiscoveryBatchData
from loguru import logger

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
    
    def insertOrUpdateUserDetails (self, id, mail = "", parentId = "", firstName = "", familyName = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        newUser = UserData(id=id, parentId=parentId, firstName=firstName, familyName= familyName, role=role, mailAddress=mail, motivations=motivations, personsOfInterest=personsOfInterest)
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
        motivationCollection = db["motivationsTest"]

        motivationDataJSON = motivationCollection.find_one({"id" : id})

        if (motivationDataJSON is None):
            return None

        # print ("motivation data is {0}", motivationDataJSON)

        motivationTextsDic = self.getTextDataByParent(id, locale)

        newMotivtion = motivationData()
        newMotivtion.buildFromJSON(motivationDataJSON, motivationTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return newMotivtion 
    
    def getAllMotivationsIds(self):
        db = self.getDatabase()
        motivationCollection = db["motivationsTest"]

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

        # get id's for text quesry
        parentsIds = ([p["id"] for p in questionsDataJSON["possibleResponses"]])
        parentsIds.append(questionsDataJSON["id"])

        questionTextsDic = None
        
        if (locale != 0):
            # get localed text
            logger.debug ("retrieving texts data")
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
#insertMotivation()
#getMotivation("M001", LOCALE_HEB_MA)
