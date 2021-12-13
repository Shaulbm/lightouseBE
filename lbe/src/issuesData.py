import jsonpickle
import json

class MotivationsRelationType:
    CONTRIBUTING_MOTIVATIONS = 0
    RESOLVING_MOTIVATIONS = 1

class SubjectData:
    def __init__(self, id = "", name = "", description = ""):
        self.id = id
        self.name = name
        self.description = description

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.description = localedTextDic[jsonData["description"]]
        else:
            # build as is
            self.name = jsonData["name"]
            self.description = jsonData["description"]

class RelatedMotivationData:
    def __init__(self, id = "", issueId = "", motivationId = "", impact = "", text = "", moovExplanation = ""):
        self.id = id
        self.issueId = issueId
        self.motivationId = motivationId
        self.impact = impact
        self.text = text
        self.moovExplanation = moovExplanation

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJSON(self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.issueId = jsonData["issueId"]
        self.motivationId = jsonData["motivationId"]
        self.impact = int(jsonData["impact"])
        
        if (localedTextDic is not None):
            self.text = localedTextDic[jsonData["text"]]
            self.moovExplanation = localedTextDic[jsonData["moovExplanation"]]
        else:
            # build as is
            self.text = jsonData["text"]
            self.moovExplanation = jsonData["moovExplanation"]

class ExtendedRelatedMotivationData(RelatedMotivationData):
    def __init__(self, id = "", issueId = "", motivationId = "", motivationName= "", impact = "", text = "", moovExplanation = ""):
        super().__init__(id=id, issueId=issueId, motivationId=motivationId, impact=impact, text=text,moovExplanation=moovExplanation)
        self.motivationName = motivationName

    def toJSON(self):
        superJsonData = super().toJSON()
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        extendedJsonObject = json.loads (responseDataJSON)

        jointJSONObject = {key: value for (key, value) in (extendedJsonObject.items() + superJsonData.items())}

    def buildFromJSON(self, jsonData, localedTextDic = None):
        super().buildFromJSON(jsonData=jsonData, localedTextDic=localedTextDic)

        # motivation name is set externally and not from JSON
        self.motivationName = ""

    def buildFromBaseClass(self, relatedMotivationDetails):
        self.id = relatedMotivationDetails.id
        self.issueId = relatedMotivationDetails.issueId
        self.motivationId = relatedMotivationDetails.motivationId
        self.impact = relatedMotivationDetails.impact
        self.text = relatedMotivationDetails.text
        self.moovExplanation = relatedMotivationDetails.moovExplanation

class IssueData:
    def __init__(self, id="", subjectId = "", name = 0, shortDescription = "", longDescription = 0, contributingMotivations = [], resolvingMotivations = []):
        self.id = id
        self.subjectId = subjectId
        self.name = name
        self.shortDescription = shortDescription
        self.longDescription = longDescription
        self.contributingMotivations = contributingMotivations.copy()
        self.resolvingMotivations = resolvingMotivations.copy()

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.subjectId = jsonData["subjectId"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.shortDescription = localedTextDic[jsonData["shortDescription"]]
            self.longDescription = localedTextDic[jsonData["longDescription"]]
        else:
            # create as is
            self.name = jsonData["name"]
            self.shortDescription = jsonData["shortDescription"]
            self.longDescription = jsonData["longDescription"]
        
        self.buildRelatedMotivations(jsonData=jsonData, localedTextDic=localedTextDic)


    def buildRelatedMotivations (self, jsonData, localedTextDic = None):
        self.contributingMotivations = []

        for currContributingMotivation in jsonData["contributingMotivations"]:
            contributingMotivation = RelatedMotivationData()
            contributingMotivation.buildFromJSON(currContributingMotivation, localedTextDic)

            self.contributingMotivations.append(contributingMotivation)

        self.resolvingMotivations = []

        for currResolvingMotivation in jsonData["resolvingMotivations"]:
            resolvingMotivation = RelatedMotivationData()
            resolvingMotivation.buildFromJSON(currResolvingMotivation, localedTextDic)

            self.resolvingMotivations.append(resolvingMotivation)

class IssueExtendedData(IssueData):
    def __init__(self, id="", subjectId = "", name = 0, shortDescription = "", longDescription = 0, contributingMotivations = [], resolvingMotivations = []):
        super().__init__(id=id, subjectId=subjectId,name=name, shortDescription=shortDescription, longDescription=longDescription, contributingMotivations=contributingMotivations, resolvingMotivations=resolvingMotivations)

    def buildRelatedMotivations (self, jsonData, localedTextDic = None):
        self.contributingMotivations = []

        for currContributingMotivation in jsonData["contributingMotivations"]:
            contributingMotivation = ExtendedRelatedMotivationData()
            contributingMotivation.buildFromJSON(currContributingMotivation, localedTextDic)

            self.contributingMotivations.append(contributingMotivation)

        self.resolvingMotivations = []

        for currResolvingMotivation in jsonData["resolvingMotivations"]:
            resolvingMotivation = ExtendedRelatedMotivationData()
            resolvingMotivation.buildFromJSON(currResolvingMotivation, localedTextDic)

            self.resolvingMotivations.append(resolvingMotivation)

    def copyFromBaseClass (self, issueDetails):
        self.id = issueDetails.id
        self.subjectId = issueDetails.subjectId
        self.name = issueDetails.name
        self.shortDescription = issueDetails.shortDescription
        self.longDescription = issueDetails.longDescription

        self.contributingMotivations = []
        self.resolvingMotivations = []

        for currRelatedMotivation in issueDetails.contributingMotivations:
            currExtendedRelatedMotivation = ExtendedRelatedMotivationData()
            currExtendedRelatedMotivation.buildFromBaseClass(currRelatedMotivation)
            self.contributingMotivations.append(currExtendedRelatedMotivation)

        for currRelatedMotivation in issueDetails.resolvingMotivations:
            currExtendedRelatedMotivation = ExtendedRelatedMotivationData()
            currExtendedRelatedMotivation.buildFromBaseClass(currRelatedMotivation)
            self.resolvingMotivations.append(currExtendedRelatedMotivation)

class IssuePartialData:
    def __init__(self, id="", subjectId = "", name = 0, shortDescription = "", longDescription = 0):
        self.id = id
        self.subjectId = subjectId
        self.name = name
        self.shortDescription = shortDescription
        
    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.subjectId = jsonData["subjectId"]

        if (localedTextDic is not None):
            self.name = localedTextDic[jsonData["name"]]
            self.shortDescription = localedTextDic[jsonData["shortDescription"]]
        else:
            # create as is
            self.name = jsonData["name"]
            self.shortDescription = jsonData["shortDescription"]        

class MoovInstance:
    def __init__(self, id = "", userId = "", counterpartId = "", moovId = "", issueId = "", startDate= "", endDate="", feedbackScore = 0, feedbackText = ""):
        self.id = id
        self.userId = userId
        self.counterpartId = counterpartId
        self.moovId = moovId
        self.issueId = issueId
        self.startDate = startDate
        self.endDate = endDate
        self.feedbackScore = feedbackScore
        self.feedbackText = feedbackText

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.userId = jsonData["userId"]
        self.counterpartId = jsonData["counterpartId"]
        self.moovId = jsonData["moovId"]
        self.issueId = jsonData["issueId"]
        self.startDate = jsonData["startDate"]
        self.endDate = jsonData["endDate"]
        self.feedbackScore = jsonData["feedbackScore"]
        self.feedbackText = jsonData["feedbackText"]

class ConflictData:
    def __init__(self, id = "", motivationId = "", motivationCounterpartId = "", score = 0, description = "", relationType = MotivationsRelationType.CONTRIBUTING_MOTIVATIONS) -> None:
        self.id = id
        self.motivationId = motivationId
        self.motivationCounterpartId = motivationCounterpartId
        self.score = score
        self.description = description
        self.relationType = relationType

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic=None):
        self.id = jsonData["id"]
        self.motivationId = jsonData["motivationId"]
        self.motivationCounterpartId = jsonData["motivationCounterpartId"]
        self.score = jsonData["score"]
        self.relationType = jsonData["relationType"]
        
        if (localedTextDic is not None):
            self.description = localedTextDic[jsonData["description"]]
        else:
            # create as is
            self.description = jsonData["description"]     
    
class ExtendedMoovInstance(MoovInstance):
    def __init__(self, id = "", userId = "", counterpartId = "", moovId = "", issueId = "", startDate= "", endDate="", feedbackScore = 0, feedbackText = "", moovData = None):
        super().__init__(id=id, userId=userId,counterpartId=counterpartId,moovId=moovId,issueId=issueId,startDate=startDate, endDate=endDate, feedbackScore=feedbackScore, feedbackText=feedbackText)
        self.moovData = moovData
