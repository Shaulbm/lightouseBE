import jsonpickle
import json

class QuestionsType:
    REGULAR = 1
    TEXT_ONLY = 2
    MOTIVATION_GAP = 3

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
    def __init__(self, id="", idx = 0, batchId = "", batchIdx = 0, setId = "", setIdx = 0, type = QuestionsType.REGULAR, questionText = "", userResponsesNo = 0, motivationId= "", imageUrl = "", possibleResponses = []):
        self.id = id
        self.idx = idx
        self.batchId = batchId
        self.batchIdx = batchIdx
        self.setId = setId
        self.setIdx = setIdx
        self.type = type
        self.userResponsesNo = userResponsesNo
        self.motivationId = motivationId
        self.imageURL = imageUrl
        self.questionText = questionText
        self.possibleResponses = possibleResponses.copy()

    def toJSON (self):
        questionDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (questionDataJSON)

        return jsonObject

    def buildFromJSON (self, jsonData, localedTextDic = None):
        self.id = jsonData["id"]
        self.batchId = jsonData["batchId"]
        self.idx = int(jsonData["idx"])
        self.batchIdx = int(jsonData["batchIdx"])
        self.setId = jsonData["setId"]
        self.setIdx = int(jsonData["setIdx"])
        self.type = int (jsonData["type"]) 
        self.userResponsesNo = int(jsonData["userResponsesNo"])
        self.motivationId = jsonData["motivationId"]
        self.imageURL = jsonData["imageURL"]

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
