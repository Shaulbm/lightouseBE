import json
import jsonpickle

class UserRoles:
    NONE = 0
    EMPLOYEE = 1
    MANAGER = 2
    HR = 3

class TextData:
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

class UserData:
    def __init__(self, id = "", parentId = "", firstName = "", familyName = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
        self.id = id
        self.parentId = parentId
        self.firstName = firstName
        self.familyName = familyName
        self.role = role
        self.mailAddress = mailAddress
        self.motivations = motivations.copy()
        self.personsOfInterest = personsOfInterest.copy()

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.parentId = jsonData["parentId"]
        self.firstName = jsonData["firstName"]
        self.familyName = jsonData["familyName"]
        self.role = jsonData["role"]
        self.mailAddress = jsonData["mailAddress"]

        if len(jsonData["motivations"]) > 0:
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}

        if len(jsonData["personsOfInterest"]) > 0:
            self.personsOfInterest = jsonData["personsOfInterest"].copy()
        else:
            self.personsOfInterest = []
