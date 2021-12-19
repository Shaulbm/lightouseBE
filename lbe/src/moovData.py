import jsonpickle
import json


class MoovData:
    def __init__(self, id = "", issueId = "", motivationId = "", score = 0, image = "", name = "", description = "", howTo="", contributorId = ""):
        self.id = id
        self.issueId = issueId
        self.motivationId = motivationId
        self.score = score
        self.image = image
        self.name = name
        self.description = description
        self.howTo = howTo
        self.contributorId = contributorId

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.issueId = jsonData["issueId"]
        self.motivationId = jsonData["motivationId"]
        self.score = jsonData["score"]
        self.image = jsonData["image"]
        self.contributorId = jsonData["contributorId"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.description = localedTextDic[jsonData["description"]]
            self.howTo = localedTextDic[jsonData["howTo"]]
        else:
            # build as is
            self.name = jsonData["name"]
            self.description = jsonData["description"]
            self.howTo = jsonData["howTo"]

class ConflictMoovData:
    def __init__(self, id = "", conflictId = "", score=0, image="", contributor="", name="", description="", howTo="", reasoning=""):
        self.id = id
        self.conflictId = conflictId
        self.score = score
        self.image = image
        self.contributor = contributor
        self.name = name
        self.description = description
        self.howTo = howTo
        self.reasoning = reasoning
        
    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic=None):
        self.id = jsonData["id"]
        self.conflictId = jsonData["conflictId"]
        self.score = jsonData["score"]
        self.image = jsonData["image"]
        self.contributor = jsonData["contributor"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.description = localedTextDic[jsonData["description"]]
            self.howTo = localedTextDic[jsonData["howTo"]]
            self.reasoning = localedTextDic[jsonData["reasoning"]]
        else:
            # create as is
            self.name = jsonData["name"]
            self.description = jsonData["description"]
            self.howTo = jsonData["howTo"]
            self.reasoning = jsonData["resoning"]