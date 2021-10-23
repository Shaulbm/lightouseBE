from collections import namedtuple
import json
import jsonpickle

class UserDiscoveryJourneyData:
    def __init__(self, id ="", journeyId = "", userId = "", status = "", currBatch = "", lastAnsweredQuestion = "", userResponses = {}):
        self.id = id
        self.journeyId = journeyId
        self.userId = userId
        self.status = status
        self.currBatch = currBatch
        self.lastAnsweredQuestion = lastAnsweredQuestion
        self.userResponses = userResponses

    def buildFromJSON (self, jsonData):
        try:
            self.id = jsonData["id"]
            self.journeyId = jsonData["journeyId"]
            self.userId = jsonData["userId"]
            self.status = jsonData["status"]
            self.currBatch = jsonData["currBatch"]
            self.lastAnsweredQuestion = jsonData["lastAnsweredQuestion"]
            self.userResponses = json.loads(jsonData["userResponses"])

        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load user discovery data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJSON(self):
        userDiscoveryDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDiscoveryDataJSON)

        return jsonObject

class DiscoveryBatchData:
    def __init__(self, journeyId = "", batchId = "", batchIdx = 0, imageUrl = "", text=""):
        self.journeyId = journeyId
        self.batchId = batchId
        self.batchIdx = batchIdx
        self.imageUrl = imageUrl
        self.text = text

    def buildFromJSON (self, jsonData, localedTextDic):
        # jsonDataStr = json_util.dumps(jsonData)
        # print (jsonDataStr)
        # motivtionObj = json.loads(jsonDataStr, object_hook=motivationDecoder)

        try:
            self.journeyId = jsonData["journeyId"]
            self.batchId = jsonData["batchId"]
            self.batchIdx = jsonData["batchIdx"]
            self.imageUrl = jsonData["imageUrl"]
            self.text = localedTextDic[jsonData["text"]]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load discovery data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJSON(self):
        userDiscoveryDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDiscoveryDataJSON)

        return jsonObject

class TailResolutionData:
    def __init__(self, motivationsToResolveCount = 0, motivationsList = []):
        self.motivationsToResovleCount = motivationsToResolveCount
        self.motivationsList = motivationsList.copy()

