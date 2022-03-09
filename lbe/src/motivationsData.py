from collections import namedtuple
import json
import jsonpickle

class InsightsUserType:
    GENERAL = 0
    TEAM_MEMBER = 1
    SELF = 2

class InsightTypeData:
    def __init__(self):
        self.id = "",
        self.type = InsightsUserType.GENERAL
        self.text = ""

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic):
        self.id = jsonData["id"]
        self.type = jsonData["type"]
        self.text = localedTextDic[jsonData["text"]]

class MotivationInsightData:
    def __init__(self):
        self.id = ""
        self.motivationId = ""
        self.insightId = ""
        self.type = 0
        self.shortDescription = ""
        self.longDescription = ""

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic):
        self.id = jsonData["id"]
        self.motivationId = jsonData["motivationId"]
        self.insightId = jsonData["insightId"]
        self.type = jsonData["type"]
        self.shortDescription = localedTextDic[jsonData["shortDescription"]]
        self.longDescription = localedTextDic[jsonData["longDescription"]]

class InsightAggregationData:
    def __init__(self):
        self.insightType = InsightTypeData()
        self.insights = []

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

class MotivationData:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.shortDescription = ""
        self.longDescription = ""
        self.additionalData = ""
        self.imageUrl = ""
        self.color = ""
        self.tailResolution = ""
        self.insights = []

    def buildFromJSON (self, jsonData, localedTextDic):
        self.id = jsonData["id"]
        self.name =  localedTextDic[jsonData["name"]]
        self.shortDescription = localedTextDic[jsonData["shortDescription"]]
        self.longDescription = localedTextDic[jsonData["longDescription"]]
        self.imageUrl = jsonData["imageUrl"]
        self.color = jsonData["color"]
        self.tailResolution = localedTextDic[jsonData["tailResolution"]]

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

class MotivationPartialData:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.shortDescription = ""
        self.imageUrl = ""
        self.color = ""

    def buildFromJSON (self, jsonData, localedTextDic):
        try:
            self.id = jsonData["id"]
            self.name =  localedTextDic[jsonData["name"]]
            self.shortDescription = localedTextDic[jsonData["shortDescription"]]
            self.imageUrl = jsonData["imageUrl"]
            self.color = jsonData["color"]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load motivation data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

