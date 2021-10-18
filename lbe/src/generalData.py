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
            self.id = jsonData["id"]
            self.contentText = jsonData["contentText"]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load text data from JSON, data is {0}, error is {1}", jsonData, err))

class userData:
    def __init__(self, id = "", parentId = "", mailAddress = "", motivations = None):
        self.id = id
        self.parentId = parentId
        self.mailAddress = mailAddress
        self.motivations = {}

        if (motivations is not None):
            self.motivations = motivations.copy()

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.parentId = jsonData["parentId"]
        self.mailAddress = jsonData["mailAddress"]

        if (len(jsonData["motivations"]) > 0):
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}
