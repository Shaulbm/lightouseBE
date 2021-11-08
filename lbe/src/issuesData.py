import jsonpickle
import json

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
    def __init__(self, id = "", issueId = "", motivationId = "", impact = "", text = ""):
        self.id = id
        self.issueId = issueId
        self.motivationId = motivationId
        self.impact = impact
        self.text = text

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
        else:
            # build as is
            self.text = jsonData["text"]

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
        
        self.contributingMotivations = []

        for currContributingMotivation in jsonData["contributingMotivations"]:
            contributingMotivation = RelatedMotivationData()
            contributingMotivation.buildFromJSON(currContributingMotivation, localedTextDic)

            self.contributingMotivations.append(contributingMotivation)

        for currResolvingMotivation in jsonData["resolvingMotivations"]:
            resolvingMotivation = RelatedMotivationData()
            resolvingMotivation.buildFromJSON(currResolvingMotivation, localedTextDic)

            self.resolvingMotivations.append(resolvingMotivation)
