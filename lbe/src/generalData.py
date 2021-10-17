import json
import jsonpickle

class textData:
    def __init__(self, parentId = "", Id = "", contentText = ""):
        self.parentId = parentId
        self.id = Id
        self.text = contentText

    def toJSON(self):
        textDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (textDataJSON)

        return jsonObject

    def fromJSON (self, jsonData):
        try:
            self.parentId = jsonData["parentId"]
            self.id = jsonData["textId"]
            self.contentText = jsonData["contentText"]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load text data from JSON, data is {0}, error is {1}", jsonData, err))