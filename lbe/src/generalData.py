from cmath import cos
import datetime
import json
from xmlrpc.client import DateTime
import bson
import jsonpickle
from numpy import full

class TrialState:
    ACTIVE = 0
    DONE = 1

class UserState:
    ACTIVE = 0
    SUSPENDED = 1
    DELETED = 2

class AccountType:
    REGULAR = 1
    TRIAL = 2
class UserRoles:
    NONE = 0
    EMPLOYEE = 1
    MANAGER = 2
    HR = 3

class ClaroRoles:
    REGULAR = 100
    POWER_USER = 200
    ADMINISTRATOR = 1000

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
    ONGOING = 2

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
    def __init__(self, id = "", state = UserState.ACTIVE, accountType = AccountType.REGULAR, parentId = "", firstName = "", familyName = "", discoveryStatus= DiscoveryStatus.UNDISCOVERED, orgId = "", role = UserRoles.NONE, claroRole = ClaroRoles.REGULAR, gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, color = "", mailAddress = "", presentGuidedTours = False, presentFullHierarchy = False, motivations = {}, personsOfInterest = [], privacyApprovalDate = ""):
        self.id = id
        self.state = state
        self.accountType = accountType
        self.parentId = parentId
        self.firstName = firstName
        self.familyName = familyName
        self.discoveryStatus = discoveryStatus
        self.orgId = orgId
        self.role = role
        self.claroRole = claroRole
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
        self.color = color
        self.mailAddress = mailAddress
        self.presentGuidedTours = presentGuidedTours
        self.presentFullHierarchy = presentFullHierarchy
        self.motivations = motivations.copy()
        self.personsOfInterest = personsOfInterest.copy()
        self.privacyApprovalDate = privacyApprovalDate

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.state = int(jsonData["state"])
        
        if ("accountType" in jsonData):
            self.accountType = int(jsonData["accountType"])
        
        
        self.parentId = jsonData["parentId"]
        self.firstName = jsonData["firstName"]
        self.familyName = jsonData["familyName"]
        self.discoveryStatus = int(jsonData["discoveryStatus"])
        self.orgId = jsonData["orgId"]
        self.role = jsonData["role"]

        if ("claroRole" in jsonData):
            self.claroRole = int(jsonData["claroRole"])

        self.gender = jsonData["gender"]
        self.locale = jsonData["locale"]
        self.isRTL = bool(jsonData["isRTL"])
        self.color = jsonData["color"]
        self.mailAddress = jsonData["mailAddress"]

        if ("presentFullHierarchy" in jsonData):
            self.presentFullHierarchy = bool(jsonData["presentFullHierarchy"])

        if ("presentGuidedTours" in jsonData):
            self.presentGuidedTours = bool(jsonData["presentGuidedTours"])

        if ("privacyApprovalDate" in jsonData):
            self.privacyApprovalDate = jsonData["privacyApprovalDate"]
        else:
            self.privacyApprovalDate = ""

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
    def __init__(self, id = "", firstName = "", familyName = "", mailAddress="", discoveryStatus = DiscoveryStatus.UNDISCOVERED, role=UserRoles.NONE, gender = Gender.MALE, locale = Locale.UNKNOWN, isRTL = False, color = "", orgId = "", presentFullHierarchy = False, motivations = [], activeMoovsNo = 0, recommendedMoovsNo = 0):
        self.id = id
        self.firstName = firstName
        self.familyName = familyName
        self.mailAddress = mailAddress
        self.discoveryStatus = discoveryStatus
        self.role = role
        self.gender = gender
        self.locale = locale
        self.isRTL = isRTL
        self.color = color
        self.orgId = orgId
        self.presentFullHierarchy = presentFullHierarchy
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
        self.mailAddress = jsonData["mailAddress"]
        self.discoveryStatus = int(jsonData["discoveryStatus"])
        self.role = int(jsonData["role"])
        self.gender = jsonData["gender"]
        self.locale = jsonData["locale"]
        self.isRTL = bool(jsonData["isRTL"])
        self.color = jsonData["color"]
        self.orgId = jsonData["orgId"]
        self.presentFullHierarchy = jsonData["presentFullHierarchy"]

        if len(jsonData["motivations"]) > 0:
            self.motivations = jsonData["motivations"].copy()
        else:
            self.motivations = {}

    def fromFullDetails (self, fullUserDetails : UserData):
        # active and recommended moovs are not in the full data and will not be copied
        self.id = fullUserDetails.id
        self.firstName = fullUserDetails.firstName
        self.familyName = fullUserDetails.familyName
        self.mailAddress = fullUserDetails.mailAddress
        self.discoveryStatus = fullUserDetails.discoveryStatus
        self.role = fullUserDetails.role
        self.gender = fullUserDetails.gender
        self.locale = fullUserDetails.locale
        self.isRTL = fullUserDetails.isRTL
        self.color = fullUserDetails.color
        self.orgId = fullUserDetails.orgId
        self.presentFullHierarchy = fullUserDetails.presentFullHierarchy

        if len(fullUserDetails.motivations) > 0:
            self.motivations = fullUserDetails.motivations.copy()
        else:
            self.motivations = {}

class UserCredData:
    def __init__(self, id ="", orgId ="", password=""):
        self.id = id
        self.orgId = orgId
        self.password = password
        pass

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.orgId = jsonData["orgId"]
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

class TrialData:
    def __init__(self, id = "", orgName="", userMail = "", startDate = datetime.datetime.utcnow(), plannedEndDate = datetime.datetime.utcnow()):
        self.id = id
        self.orgName = orgName
        self.userMail = userMail
        self.startDate = startDate
        self.plannedEndDate = plannedEndDate

    def toJSON (self):
        userDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (userDataJSON)

        return jsonObject 

    def fromJSON (self, jsonData):
        self.id = jsonData["id"]
        self.orgName =  jsonData["orgName"]
        self.userMail =  jsonData["userMail"]
        self.startDate =  jsonData["startDate"]
        self.plannedEndDate =  jsonData["plannedEndDate"]