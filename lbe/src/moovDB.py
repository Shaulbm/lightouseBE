from hashlib import new
import threading
from pymongo import MongoClient
from pymongo.common import partition_node
from lbe.src.environmentProvider import EnvKeys
from questionsData import QuestionsType
from moovData import IssueMoovData, ConflictMoovData, ExtendedConflictMoovData, MoovInstance, ExtendedMoovInstance, BaseMoovData
from motivationsData import MotivationData, MotivationPartialData
from generalData import UserData, UserPartialData, UserRoles, Gender, Locale, UserContextData, UserCredData
from questionsData import QuestionData
from singleton import Singleton
from discoveryData import UserDiscoveryJourneyData, DiscoveryBatchData
from loguru import logger
import anytree
from anytree import Node
from issuesData import IssueData, SubjectData, IssuePartialData, IssueExtendedData, ConflictData, ExtendedConflictData
import datetime
import environmentProvider as ep

ROOT_USER_IMAGES_PATH = 'C:\\Dev\\Data\\UserImages'
DEFAULT_USER_IMAGES_DIR = 'Default'
DAYS_TO_COMPLETE_MOOV = 7

class MoovDBInstance(metaclass=Singleton):
    def __init__(self):
        self.dataBaseInstance = None
        self.counterLock = threading.Lock()

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

    def getTextDataByParent (self, parentId, locale, gender):
        textDataCollection = self.getTextCollectionByLocale(locale, gender)
            
        allTextsArray = textDataCollection.find ({"parentId" : parentId})

        textDic = {}

        for currText in allTextsArray:
            textDic[currText["id"]] = currText["text"]

        return textDic

    def getTextDataByParents (self, parentsIds, locale, gender):
        resultTextDict = {}
        for currParrentId in parentsIds:
            resultTextDict = resultTextDict | self.getTextDataByParent(currParrentId, locale, gender)

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

    def insertOrUpdateMotivation (self, motivationDataObj):
        db = self.getDatabase()
        motivationsCollection = db["motivations"]
        motivationDataJSON = motivationsCollection.find_one({"id" : motivationDataObj.id})

        if (motivationDataJSON is not None):
            #object found
            motivationFilter = {'id':motivationDataObj.id}
            motivationsCollection.replace_one (motivationFilter, motivationDataObj.toJSON())
        else:
            # this is a new motivation
            motivationsCollection.insert_one(motivationDataObj.toJSON())

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
        # db = self.getDatabase()
        # moovsCollection = db["moovs"]

        # moovDataJSON = moovsCollection.find_one({"id" : id})

        # if (moovDataJSON is None):
        #     return None

        # moovTextsDic = None
        # if (userContext.locale is not None):
        #     moovTextsDic = self.getTextDataByParent(id, userContext.locale)

        # newMoov = IssueMoovData()
        # newMoov.buildFromJSON(moovDataJSON, moovTextsDic)

        # return newMoov 
        pass

    def getBaseMoov (self, id, userContext: UserContextData):
        db = self.getDatabase()
        moovsCollection = db["moovs"]

        moovDataJSON = moovsCollection.find_one({"id" : id})

        if (moovDataJSON is None):
            return None

        moovTextsDic = None
        if (userContext is not None):
            moovTextsDic = self.getTextDataByParent(id, userContext.locale, userContext.gender)

        foundMoov = BaseMoovData()
        foundMoov.buildFromJSON(moovDataJSON, moovTextsDic)

        return foundMoov 

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
            moovTextsDic = self.getTextDataByParent(currMoovJSONData["id"], userContext.locale, userContext.gender)
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

        motivationTextsDic = self.getTextDataByParent(id, userContext.locale, userContext.gender)

        foundMotivation = MotivationData()
        foundMotivation.buildFromJSON(motivationDataJSON, motivationTextsDic)

        # print ("motivation object is {0}", newMotivtion.toJSON())
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

    # def userLogin(self, userMail, password):
    #     userDetails : UserData = self.getDBUserByMail(mail=userMail)

    #     # TBD verify password
    #     # for now password is always true

    #     partialUserDetails = None

    #     if (userDetails is not None):
    #         hashedPassword = hashlib.sha256(password.encode('utf-8'))
    #         if self.getUserPassword(userDetails.id) == hashedPassword.hexdigest():
    #             partialUserDetails = UserPartialData()
    #             partialUserDetails.fromFullDetails(userDetails)
    #         else:
    #             # raise error 404
    #             pass
        
    #     return partialUserDetails

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

    def getUserByMail (self, mail):
        db = self.getDatabase()
        usersCollection = db["users"]

        userFilter = {"mailAddress":mail}

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
                questionTextsDic = self.getTextDataByParent(foundQuestion["id"], userContext.locale, userContext.gender)

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
            issuesTextsDic = self.getTextDataByParents(parentsIds, userContext.locale, userContext.gender)

        issueDetails = IssueData()
        issueDetails.buildFromJSON(jsonData = issueDataJSON, localedTextDic=issuesTextsDic)

        return issueDetails

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
        
        if (userContext.locale != Locale.UNKNOWN):
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
    
    def getAllIssues (self, userContext: UserContextData):
        db = self.getDatabase()
        subjectsCollection = db["issues"]

        issuesDataJSONList = subjectsCollection.find()

        issuesDetailsList = []

        for currIssueJSONData in issuesDataJSONList:
            issueTextsDic = self.getTextDataByParent(currIssueJSONData["id"], userContext.locale, userContext.gender)
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

    #return the users that the given UserId is in their POI
    def getInterestedusers(self, userId):
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

        moovData = self.getBaseMoov(moovId, userContext=userContext)

        #Check if there is an already moovId with userId and teamMember Id that is active
        existingMoov = self.getActiveMoovByMoovUserAndCounterpart(userId=userId, moovId=moovId, counterpartId=counterpartId)

        if existingMoov is not None:
            #rasie error active Moov already exists
            return existingMoov

        newActiveMoov = MoovInstance()
        newActiveMoov.id = "AM_" + str(self.getNextCount())
        newActiveMoov.moovId = moovId
        newActiveMoov.userId = userId
        newActiveMoov.counterpartsIds.append(counterpartId)
        newActiveMoov.priority = priority
        newActiveMoov.startDate = datetime.datetime.utcnow()
        newActiveMoov.plannedEndDate = newActiveMoov.startDate + datetime.timedelta(days=ep.getAttribute(EnvKeys.behaviour, EnvKeys.daysToAccomplishActiveMoov))
        
        activeMoovsCollection.insert_one(newActiveMoov.toJSON())

        return newActiveMoov

    def activateConflictMoov (self, moovId, userId, counterpartsIds, priority, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        moovData = self.getBaseMoov(moovId, userContext=userContext)

        #Check if there is an already moovId with userId and teamMember Id that is active
        existingMoov = self.getActiveMoovByMoovUserAndMultipleCounterparts(userId=userId, moovId=moovId, counterpartsIds=counterpartsIds)

        if existingMoov is not None:
            #rasie error active Moov already exists
            return existingMoov

        newActiveMoov = MoovInstance()
        newActiveMoov.id = "AM_" + str(self.getNextCount())
        newActiveMoov.moovId = moovId
        newActiveMoov.userId = userId
        newActiveMoov.counterpartsIds = counterpartsIds.copy()
        newActiveMoov.priority = priority
        newActiveMoov.startDate = datetime.datetime.utcnow()
        newActiveMoov.plannedEndDate = newActiveMoov.startDate + datetime.timedelta(days=DAYS_TO_COMPLETE_MOOV)
        
        activeMoovsCollection.insert_one(newActiveMoov.toJSON())

        return newActiveMoov

    def getActiveMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "counterpartsIds": counterpartId}

        activeMoovsDataJSONList = activeMoovsCollection.find(activeMoovFilter)

        if (activeMoovsDataJSONList is None):
            return None

        foundActiveMoovs = []
        for currActiveMoovJSONData in activeMoovsDataJSONList:
            foundAcvtiveMoov = ExtendedMoovInstance()
            foundAcvtiveMoov.buildFromJSON(currActiveMoovJSONData)
            foundAcvtiveMoov.moovData = self.getBaseMoov(foundAcvtiveMoov.moovId, userContext)
            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getPastMoovsToCounterpart (self, userId, counterpartId, userContext: UserContextData):
        db = self.getDatabase()
        historicMoovsCollection = db["historicMoovs"]

        historicMoovFilter = {"userId":userId, "counterpartsIds": counterpartId}

        historicMoovsDataJSONList = historicMoovsCollection.find(historicMoovFilter)

        if (historicMoovsDataJSONList is None):
            return None

        foundHistoricMoovs = []
        for currHistoricMoovJSONData in historicMoovsDataJSONList:
            foundHistoricMoov = ExtendedMoovInstance()
            foundHistoricMoov.buildFromJSON(currHistoricMoovJSONData)
            foundHistoricMoov.moovData = self.getBaseMoov(foundHistoricMoov.moovId, userContext)
            foundHistoricMoovs.append(foundHistoricMoov)
   
        return foundHistoricMoovs


    def getActiveMoovsForUser (self, userId, userContext: UserContextData):
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
            foundAcvtiveMoov.moovData = self.getBaseMoov(foundAcvtiveMoov.moovId, userContext)
            foundActiveMoovs.append(foundAcvtiveMoov)
   
        return foundActiveMoovs

    def getActiveMoovByMoovUserAndCounterpart(self, userId, moovId, counterpartId):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "moovId":moovId,"counterpartsIds": counterpartId}

        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter)

        if (activeMoovJSONData is None):
            return None

        foundActiveMoov = MoovInstance()
        foundActiveMoov.buildFromJSON(activeMoovJSONData)
   
        return foundActiveMoov

    def getActiveMoovByMoovUserAndMultipleCounterparts(self, userId, moovId, counterpartsIds):
        db = self.getDatabase()
        activeMoovsCollection = db["activeMoovs"]

        activeMoovFilter = {"userId":userId, "moovId":moovId,"counterpartsIds": {"$all": counterpartsIds}}

        activeMoovJSONData = activeMoovsCollection.find_one(activeMoovFilter)

        if (activeMoovJSONData is None):
            return None

        foundActiveMoov = MoovInstance()
        foundActiveMoov.buildFromJSON(activeMoovJSONData)
   
        return foundActiveMoov

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
            conflictDataFilter = {"id" : moovInstance.id}
            activeMoovsCollection.replace_one(conflictDataFilter, moovInstance.toJSON())