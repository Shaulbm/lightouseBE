import json
import jsonpickle

class localedText:
    def __init__(self, engText = "", hebText = ""):
        self.en = engText
        self.he = hebText

class textData:
    def __init__(self, parentId = "", textId = "", contentText = ""):
        self.parentId = parentId
        self.textId = textId
        self.text = contentText

    def toJson(self):
        textDataJSON = jsonpickle.encode(self, unpicklable=False)

        return json.loads (textDataJSON)

    def fromJSON (self, jsonData):
        try:
            self.parentId = jsonData["parentId"]
            self.textId = jsonData["textId"]
            self.contentText = jsonData["contentText"]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load text data from JSON, data is {0}, error is {1}", jsonData, err))