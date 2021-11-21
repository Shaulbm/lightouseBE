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