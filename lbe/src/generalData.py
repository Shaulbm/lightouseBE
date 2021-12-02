import json
import bson
import jsonpickle

class UserRoles:
    NONE = 0
    EMPLOYEE = 1
    MANAGER = 2
    HR = 3

class Locale:
    UNKNOWN = 0
    LOCALE_HEB_MA = 1
    LOCALE_HEB_FE = 2
    LOCALE_EN = 3

class Gender:
    MALE = 1
    FEMALE = 2

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
    def __init__(self, id = "", parentId = "", firstName = "", familyName = "", orgId = "", role = UserRoles.NONE, gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, mailAddress = "", motivations = {}, personsOfInterest = []):
        self.id = id
        self.parentId = parentId
        self.firstName = firstName
        self.familyName = familyName
        self.orgId = orgId
        self.role = role
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
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
        self.orgId = jsonData["orgId"]
        self.role = jsonData["role"]
        self.gender = jsonData["gender"]
        self.locale = jsonData["locale"]
        self.isRTL = bool(jsonData["isRTL"])
        self.mailAddress = jsonData["mailAddress"]

        if len(jsonData["motivations"]) > 0:
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}

        if len(jsonData["personsOfInterest"]) > 0:
            self.personsOfInterest = jsonData["personsOfInterest"].copy()
        else:
            self.personsOfInterest = []

class UserPartialData:
    def __init__(self, id = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, orgId = "", motivations = []):
        self.id = id
        self.firstName = firstName
        self.familyName = familyName
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
        self.orgId = orgId
        self.motivations = motivations.copy()

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.firstName = jsonData["firstName"]
        self.familyName = jsonData["familyName"]
        self.gender = jsonData["gender"]
        self.locale = int(jsonData["locale"])
        self.isRTL = bool(jsonData["isRTL"])
        self.orgId = jsonData["orgId"]

        if len(jsonData["motivations"]) > 0:
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}

    def fromFullDetails (self, fullUserDetails : UserData):
        self.id = fullUserDetails.id
        self.firstName = fullUserDetails.firstName
        self.familyName = fullUserDetails.familyName
        self.gender = fullUserDetails.gender
        self.locale = fullUserDetails.locale
        self.isRTL = fullUserDetails.isRTL
        self.orgId = fullUserDetails.orgId

        if len(fullUserDetails.motivations) > 0:
            self.motivations = fullUserDetails.motivations.copy()
        else:
            self.motivations = {}


class UserImageData:
    def __init__(self, userId ="", image = ""):
        self.userId = userId
        self.image = image
    
    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        # resData = {"userId": self.userId, "image": bson.Binary(jsonpickle.dumps(self.image))}

        resData = {"userId": self.userId, "image": bson.Binary(self.image)}
        return resData 

    def fromJSON (self, jsonData):
        self.userId = jsonData["userId"]
        self.image = jsonpickle.loads(jsonData["image"])

class OrgData:
    def __init__(self, id = "", name = "", url = ""):
        self.id = id
        self.name = name
        self.url = url 

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.name = jsonData["name"]
        self.url = jsonData["url"]

class UserCircleData:
    def __init__(self):
        self.teamMembersList = []
        self.peopleOfInterest = []

class UserContextData:
    def __init__(self, userId = "", firstName = "", lastName = "", locale = Locale.UNKNOWN, isRTL = False):
        self.userId = userId
        self.firstName = firstName
        self.lastName = lastName
        self.locale = int(locale)
        self.isRTL = isRTL
        self.timeStamp = None

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.userId = jsonData["userId"]
        self.firstName = jsonData["firstName"]
        self.lastName = jsonData["lastName"]
        self.locale = int(jsonData["locale"])
        self.isRTL = bool(jsonData["isRTL"])
        self.timeStamp = jsonData["timeStamp"]
