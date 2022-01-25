from cmath import cos
import datetime
import json
import bson
import jsonpickle

class UserRoles:
    NONE = 0
    EMPLOYEE = 1
    MANAGER = 2
    HR = 3

class Locale:
    UNKNOWN = ""
    LOCALE_HE_IL = "he-IL"
    LOCALE_EN_US = "en-US"

class Gender:
    MALE = 1
    FEMALE = 2

class DiscoveryStatus:
    UNDISCOVERED = 0
    DISCOVERED = 1

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

class UserMotivationData:
    def __init__(self, motivationId = "", journeyScore = 0.0, gapFactor = 0.0):
        self.motivationId = motivationId
        self.journeyScore = journeyScore
        self.gapFactor = gapFactor

class UserData:
    def __init__(self, id = "", parentId = "", firstName = "", familyName = "", discoveryStatus= DiscoveryStatus.UNDISCOVERED, orgId = "", role = UserRoles.NONE, gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, color = "", mailAddress = "", motivations = {}, personsOfInterest = []):
        self.id = id
        self.parentId = parentId
        self.firstName = firstName
        self.familyName = familyName
        self.discoveryStatus = discoveryStatus
        self.orgId = orgId
        self.role = role
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
        self.color = color
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
        self.discoveryStatus = int(jsonData["discoveryStatus"])
        self.orgId = jsonData["orgId"]
        self.role = jsonData["role"]
        self.gender = jsonData["gender"]
        self.locale = jsonData["locale"]
        self.isRTL = bool(jsonData["isRTL"])
        self.color = jsonData["color"]
        self.mailAddress = jsonData["mailAddress"]
        self.motivations = {}

        if len(jsonData["motivations"]) > 0:
            for key, value in jsonData["motivations"].items():
                currMotivationDetails = UserMotivationData(motivationId=key, journeyScore=value["journeyScore"], gapFactor=value["gapFactor"])
                self.motivations[currMotivationDetails.motivationId] = currMotivationDetails

        if len(jsonData["personsOfInterest"]) > 0:
            self.personsOfInterest = jsonData["personsOfInterest"].copy()
        else:
            self.personsOfInterest = []

class UserPartialData:
    def __init__(self, id = "", firstName = "", familyName = "", discoveryStatus = DiscoveryStatus.UNDISCOVERED, gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, color = "", orgId = "", motivations = [], activeMoovsNo = 0, recommendedMoovsNo = 0):
        self.id = id
        self.firstName = firstName
        self.familyName = familyName
        self.discoveryStatus = discoveryStatus
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
        self.color = color
        self.orgId = orgId
        self.motivations = motivations.copy()
        self.activeMoovsCount = activeMoovsNo
        self.recommendedMoovsCount = recommendedMoovsNo

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        # active and recommended Moovs number are not in the DB hence will not be read from JSON
        self.id = jsonData["id"]
        self.firstName = jsonData["firstName"]
        self.familyName = jsonData["familyName"]
        self.discoveryStatus = int(jsonData["discoveryStatus"])
        self.gender = jsonData["gender"]
        self.locale = jsonData["locale"]
        self.isRTL = bool(jsonData["isRTL"])
        self.color = jsonData["color"]
        self.orgId = jsonData["orgId"]

        if len(jsonData["motivations"]) > 0:
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}

    def fromFullDetails (self, fullUserDetails : UserData):
        # active and recommended moovs are not in the full data and will not be copied
        self.id = fullUserDetails.id
        self.firstName = fullUserDetails.firstName
        self.familyName = fullUserDetails.familyName
        self.discoveryStatus = fullUserDetails.discoveryStatus
        self.gender = fullUserDetails.gender
        self.locale = fullUserDetails.locale
        self.isRTL = fullUserDetails.isRTL
        self.color = fullUserDetails.color
        self.orgId = fullUserDetails.orgId

        if len(fullUserDetails.motivations) > 0:
            self.motivations = fullUserDetails.motivations.copy()
        else:
            self.motivations = {}

class UserCredData:
    def __init__(self, id ="", password=""):
        self.id = id
        self.password = password
        pass

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.password = jsonData["password"]

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

class UserRelationshipData:
    def __init__(self, userId = "", counterpartId = "", costOfSeperation = 0, chanceOfSeperation = 0, timeStamp = datetime.datetime.utcnow()):
        self.userId = userId
        self.counterpartId = counterpartId
        self.costOfSeperation = costOfSeperation
        self.chanceOfSeperation = chanceOfSeperation
        self.timeStamp = timeStamp

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.userId = jsonData["userId"]
        self.counterpartId = jsonData["counterpartId"]
        self.costOfSeperation = jsonData["costOfSeperation"]
        self.seperationChanceEstimation = jsonData["chanceOfSeperation"]
        self.timeStamp = jsonData["timeStamp"]

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
    def __init__(self, userId = "", firstName = "", lastName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False):
        self.userId = userId
        self.firstName = firstName
        self.lastName = lastName
        self.gender = gender
        self.locale = locale
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
        self.gender = jsonData["gender"]
        self.locale = int(jsonData["locale"])
        self.isRTL = bool(jsonData["isRTL"])
        self.timeStamp = jsonData["timeStamp"]
