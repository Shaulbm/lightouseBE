import jsonpickle
import json

class ResponseData:
    def __init__(self, id = "", idx = "", questionId="", motivationId="", motviationScore="", responseText = ""):
        self.id = id
        self.idx = idx
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
        self.idx = jsonData["idx"]
        self.questionId = jsonData["questionId"]
        self.motivationId = jsonData["motivationId"]
        self.motivationScore = jsonData["motivationScore"]
        self.responseText = localedTextDic[jsonData["responseText"]]

class QuestionData:
    def __init__(self, id="", batchId = "", batchIdx = "", setId = "", setIdx ="", questionText = "", possibleResponses = []):
        self.id = id
        self.batchId = batchId
        self.batchIdx = batchIdx
        self.setId = setId
        self.setIdx = setIdx
        self.questionText = questionText
        self.possibleResponses = possibleResponses.copy()

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic):
        self.id = jsonData["id"]
        self.batchId = jsonData["batchId"]
        self.batchIdx = jsonData["batchIdx"]
        self.setId = jsonData["setId"]
        self.setIdx = jsonData["setIdx"]
        self.questionText = localedTextDic[jsonData["questionText"]]
        self.possibleResponses = []

        for currPossibleResponse in jsonData["possibleResponses"]:
            resposneData = ResponseData()
            resposneData.buildFromJson(currPossibleResponse,localedTextDic)

            self.possibleResponses.append(resposneData)
