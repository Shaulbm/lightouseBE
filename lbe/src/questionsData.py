import jsonpickle
import json

class ResponseData:
    def __init__(self, id = "", idx = 0, dependency = "", questionId="", motivationId="", motviationScore=0.0, responseText = ""):
        self.id = id
        self.idx = idx
        self.dependency = dependency
        self.questionId = questionId
        self.motivationId = motivationId
        self.motivationScore = motviationScore
        self.responseText = responseText

    def toJSON(self):
        responseDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (responseDataJSON)

        return jsonObject

    def buildFromJson(self, jsonData, localedTextDic):
        self.id = jsonData["id"]
        self.idx = int(jsonData["idx"])
        self.dependency = jsonData["dependency"]
        self.questionId = jsonData["questionId"]
        self.motivationId = jsonData["motivationId"]
        self.motivationScore = float(jsonData["motivationScore"])

        if (localedTextDic is not None):
            self.responseText = localedTextDic[jsonData["responseText"]]
        else:
            self.responseText = jsonData["responseText"]

class QuestionData:
    def __init__(self, id="", batchId = "", batchIdx = 0, setId = "", setIdx = 0, questionText = "", userResponsesNo = 0, possibleResponses = []):
        self.id = id
        self.batchId = batchId
        self.batchIdx = batchIdx
        self.setId = setId
        self.setIdx = setIdx
        self.userResponsesNo = userResponsesNo
        self.questionText = questionText
        self.possibleResponses = possibleResponses.copy()

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.batchId = jsonData["batchId"]
        self.batchIdx = int(jsonData["batchIdx"])
        self.setId = jsonData["setId"]
        self.setIdx = int(jsonData["setIdx"])
        self.userResponsesNo = int(jsonData["userResponsesNo"])

        if (localedTextDic is not None):
            self.questionText = localedTextDic[jsonData["questionText"]]
        else:
            #select as is
            self.questionText = jsonData["questionText"]
        self.possibleResponses = []

        for currPossibleResponse in jsonData["possibleResponses"]:
            resposneData = ResponseData()
            resposneData.buildFromJson(currPossibleResponse,localedTextDic)

            self.possibleResponses.append(resposneData)
