from datetime import datetime
import jsonpickle
import json

MOOV_INSTANCE_NO_SCORE = -1

class MoovInstanceEventTypes:
    LIFETIME_START = 1
    LIFETIME_END = 2
    FEEDBACK = 3
    LIFETIME_EXTENTION = 4
    USER_COMMENT = 5

class MoovInstanceEventTextId:
    LIFETIME_START = "SYS_TXT_MIE_001"
    LIFETIME_END = "SYS_TXT_MIE_002"
    TIME_EXTENTION = "SYS_TXT_MIE_003"

class BaseMoovData:
    def __init__(self, id = "", score = 0, image = "", complexity = 0, name = "", motivationId = "", description = "", issueId="", howTo="", contributor = "", reasoning=""):
        self.id = id
        self.score = score
        self.image = image
        self.complexity = complexity
        self.name = name
        self.motivationId = motivationId
        self.description = description
        self.issueId = issueId
        self.howTo = howTo
        self.contributor = contributor
        self.reasoning = reasoning

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.motivationId = jsonData["motivationId"]
        self.score = int(jsonData["score"])
        self.image = jsonData["image"]
        self.complexity = int(jsonData["complexity"])
        self.issueId = jsonData["issueId"]

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
        super().__init__(id = id, score=score, image=image, contributor=contributor, name=name, description=description, issueId = issueId, howTo=howTo, reasoning=reasoning)

    def buildFromJSON(self, jsonData, localedTextDic = None):
        super().buildFromJSON(jsonData=jsonData, localedTextDic=localedTextDic)


class ExtendedIssueMoovData(IssueMoovData):
    def __init__(self, id = "", issueId = "", motivationId = "", score = 0, image = "", name = "", description = "", howTo="", steps = [], contributor = "", reasoning=""):
        super().__init__(id = id, issueId=issueId, motivationId=motivationId, score=score, image=image, contributor=contributor, name=name, description=description, howTo=howTo, reasoning=reasoning)
        self.steps = steps.copy()

    def buildFromJSON(self, jsonData, localedTextDic = None):
        super().buildFromJSON(jsonData=jsonData, localedTextDic=localedTextDic)

        self.steps = []
        if (len(jsonData["steps"]) > 0):
            self.steps = jsonData["steps"].copy()

    def fromBase(self, moovData : BaseMoovData):
        self.id = moovData.id
        self.motivationId = moovData.motivationId
        self.score = moovData.score
        self.image = moovData.image
        self.name = moovData.name
        self.description = moovData.description
        self.howTo = moovData.howTo
        self.contributor = moovData.contributor
        self.reasoning = moovData.reasoning 

    def fromIssueMoov(self, moovData:IssueMoovData):
        self.fromBase(moovData=moovData)
        self.issueId = moovData.issueId


class MoovInstanceEvent:
    def __init__(self, timeStamp = datetime.utcnow(), type = MoovInstanceEventTypes.LIFETIME_START, content = "", score = MOOV_INSTANCE_NO_SCORE):
        self.timeStamp = timeStamp
        self.type = type
        self.content = content
        self.score = score

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.timeStamp = jsonData["timeStamp"]
        self.type = jsonData["type"]
        self.score = int(jsonData["score"])

        if (localedTextDic is not None):
            self.content = localedTextDic[jsonData["content"]]
        else:
            self.content = jsonData["content"]

class MoovInstance:
    def __init__(self, id = "", userId = "", counterpartId = "", moovId = "", priority = 0, startDate= datetime.utcnow(), endDate= datetime.utcnow(), plannedEndDate =  datetime.utcnow(), isOverdue = False, notifiedUserForOverdue = False, feedbackScore = 0, feedbackText = "", events = []):
        self.id = id
        self.userId = userId
        self.counterpartId = counterpartId
        self.moovId = moovId
        self.priority = priority
        self.startDate = startDate
        self.endDate = endDate
        self.plannedEndDate = plannedEndDate
        self.isOverdue = isOverdue
        self.notifiedUserForOverdue = False
        self.feedbackScore = feedbackScore
        self.feedbackText = feedbackText
        self.events = events

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
        self.notifiedUserForOverdue = bool(jsonData["notifiedUserForOverdue"])
        self.feedbackScore = jsonData["feedbackScore"]
        self.feedbackText = jsonData["feedbackText"]
        self.counterpartId = jsonData["counterpartId"]

        self.events = []

        if "events" in jsonData and jsonData["events"].__len__() > 0:
            for currEventJsonData in jsonData["events"]:
                currEventData = MoovInstanceEvent()
                currEventData.buildFromJSON(currEventJsonData)
                self.events.append(currEventData)

        # if len(jsonData["counterpartsIds"]) > 0:
        #     self.counterpartsIds = jsonData["counterpartsIds"].copy()
        # else:
        #     self.counterpartsIds = []

class ExtendedMoovInstance(MoovInstance):
    def __init__(self, id = "", userId = "", counterpartId = "", moovId = "", priority= 0, startDate= "", endDate="", plannedEndDate =  datetime.utcnow(), feedbackScore = 0, feedbackText = "", moovData = None, counterpartFirstName ="", counterpartLastName = "", counterpartColor="", isImportant = False):
        super().__init__(id=id, userId=userId,counterpartId=counterpartId,moovId=moovId, priority=priority, startDate=startDate, endDate=endDate, plannedEndDate=plannedEndDate, feedbackScore=feedbackScore, feedbackText=feedbackText)
        self.moovData = moovData
        self.counterpartFirstName = counterpartFirstName
        self.counterpartLastName = counterpartLastName
        self.counterpartColor = counterpartColor
        self.isImportant = isImportant