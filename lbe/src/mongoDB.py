from threading import current_thread
from typing import Text
from pymongo import MongoClient
import pymongo
import json
from motivationsData import motivationData
from generalData import textData, userData
from singleton import Singleton

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

    def getTextDataByParent (parentId, locale):
        textDataCollection = getTextCollectionByLocale(locale)
            
        allTextsArray = textDataCollection.find ({"parentId" : parentId})

        textDic = {}

        for currText in allTextsArray:
            textDic[currText["textId"]] = currText["text"]

        return textDic

    def getTextCollectionByLocale(locale):
        db = getDatabase()

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
    
    def insertOrUpdateUser (self, currUserData):
        userDataJSON = currUserData.toJSON()

        db = self.dataBaseInstance()
        usersCollection = db["users"]

        foundUser = usersCollection.find_one({"id":currUserData.id})

        if (foundUser is not None):
            #the user already exists - update the user
            userDataFilter = {"id" : currUserData.id}
            usersCollection.replace_one(userDataFilter, currUserData.toJSON())
        else:
            #this is a new user
            usersCollection.insert_one(currUserData.toJSON())


    def getMotivation (self, id, locale):
        db = self.getDatabase()
        motivationCollection = db["motivationsTest"]

        motivationDataJSON = motivationCollection.find_one({"id" : id})
        print ("motivation data is {0}", motivationDataJSON)

        motivationTextsDic = getTextDataByParent(id, locale)

        newMotivtion = motivationData()
        newMotivtion.buildFromJSON(motivationDataJSON, motivationTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
        return newMotivtion 


#insertMotivation()
#getMotivation("M001", LOCALE_HEB_MA)
