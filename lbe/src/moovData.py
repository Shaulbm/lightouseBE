from datetime import datetime
import jsonpickle
import json

class BaseMoovData:
    def __init__(self, id = "", score = 0, image = "", name = "", description = "", howTo="", contributor = "", reasoning=""):
        self.id = id
        self.score = score
        self.image = image
        self.name = name
        self.description = description
        self.howTo = howTo
        self.contributor = contributor
        self.reasoning = reasoning

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.score = jsonData["score"]
        self.image = jsonData["image"]
        self.contributorId = jsonData["contributor"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.description = localedTextDic[jsonData["description"]]
            self.howTo = localedTextDic[jsonData["howTo"]]
            self.reasoning = localedTextDic[jsonData["reasoning"]]
        else:
            # build as is
            self.name = jsonData["name"]
            self.description = jsonData["description"]
            self.howTo = jsonData["howTo"]
            self.reasoning = jsonData["reasoning"]

class ConflictMoovData(BaseMoovData):
    def __init__(self, id = "", conflictId = "", score=0, image="", contributor="", name="", description="", howTo="", reasoning=""):
        super().__init__(id = id, score=score, image=image, contributor=contributor, name=name, description=description, howTo=howTo, reasoning=reasoning)

        self.conflictId = conflictId

    def buildFromJSON (self, jsonData, localedTextDic=None):
        super().buildFromJSON(jsonData=jsonData, localedTextDic=localedTextDic)
        self.conflictId = jsonData["conflictId"]

class ExtendedConflictMoovData(ConflictMoovData):
    def __init__(self, id = "", conflictId = "", conflictScore = 0, score=0, image="", contributor="", name="", description="", howTo="", reasoning=""):
        super().__init__(id = id, conflictId=conflictId ,score=score, image=image, contributor=contributor, name=name, description=description, howTo=howTo, reasoning=reasoning)

        self.conflictScore = conflictScore


class IssueMoovData(BaseMoovData):
    def __init__(self, id = "", issueId = "", motivationId = "", score = 0, image = "", name = "", description = "", howTo="", contributor = "", reasoning=""):
        super().__init__(id = id, score=score, image=image, contributor=contributor, name=name, description=description, howTo=howTo, reasoning=reasoning)
        self.issueId = issueId
        self.motivationId = motivationId

    def buildFromJSON(self, jsonData, localedTextDic = None):
        super().buildFromJSON(jsonData=jsonData, localedTextDic=localedTextDic)
        self.issueId = jsonData["issueId"]
        self.motivationId = jsonData["motivationId"]

class MoovInstance:
    def __init__(self, id = "", userId = "", counterpartsIds = [], moovId = "", priority = 0, startDate= datetime.utcnow(), endDate= datetime.utcnow(), plannedEndDate =  datetime.utcnow(), isOverdue = False, feedbackScore = 0, feedbackText = ""):
        self.id = id
        self.userId = userId
        self.counterpartsIds = counterpartsIds.copy()
        self.moovId = moovId
        self.priority = priority
        self.startDate = startDate
        self.endDate = endDate
        self.plannedEndDate = plannedEndDate
        self.isOverdue = isOverdue
        self.feedbackScore = feedbackScore
        self.feedbackText = feedbackText

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)
        
        # forcing DateTime to json, as json
        jsonObject["startDate"] = self.startDate
        jsonObject["endDate"] = self.endDate
        jsonObject["plannedEndDate"] = self.plannedEndDate

        return jsonObject

    def buildFromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.userId = jsonData["userId"]
        self.moovId = jsonData["moovId"]
        self.priority = jsonData["priority"]

        # self.startDate = datetime.strptime(jsonData["startDate"], '%Y-%m-%dT%H:%M:%S.%f')
        self.startDate = jsonData["startDate"]
        self.endDate = jsonData["endDate"]
        self.plannedEndDate = jsonData["plannedEndDate"]
        self.isOverdue = bool(jsonData["isOverdue"])
        self.feedbackScore = jsonData["feedbackScore"]
        self.feedbackText = jsonData["feedbackText"]

        if len(jsonData["counterpartsIds"]) > 0:
            self.counterpartsIds = jsonData["counterpartsIds"].copy()
        else:
            self.counterpartsIds = []

class ExtendedMoovInstance(MoovInstance):
    def __init__(self, id = "", userId = "", counterpartsIds = [], moovId = "", priority= 0, startDate= "", endDate="", plannedEndDate =  datetime.utcnow(), feedbackScore = 0, feedbackText = "", moovData = None):
        super().__init__(id=id, userId=userId,counterpartsIds=counterpartsIds,moovId=moovId, priority=priority, startDate=startDate, endDate=endDate, plannedEndDate=plannedEndDate, feedbackScore=feedbackScore, feedbackText=feedbackText)
        self.moovData = moovData
