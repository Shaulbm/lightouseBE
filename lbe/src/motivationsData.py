from collections import namedtuple
import json
import jsonpickle

class MotivationData:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.shortDescription = ""
        self.longDescription = ""
        self.additionalData = ""
        self.imageUrl = ""
        self.color = ""
        self.tailResolution = ""

    def buildFromJSON (self, jsonData, localedTextDic):
        # jsonDataStr = json_util.dumps(jsonData)
        # print (jsonDataStr)
        # motivtionObj = json.loads(jsonDataStr, object_hook=motivationDecoder)

        try:
            self.id = jsonData["id"]
            self.name =  localedTextDic[jsonData["name"]]
            self.shortDescription = localedTextDic[jsonData["shortDescription"]]
            self.longDescription = localedTextDic[jsonData["longDescription"]]
            self.imageUrl = jsonData["imageUrl"]
            self.color = jsonData["color"]
            self.tailResolution = localedTextDic[jsonData["tailResolution"]]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load motivation data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject


class MotivationPartialData:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.shortDescription = ""
        self.imageUrl = ""
        self.color = ""

    def buildFromJSON (self, jsonData, localedTextDic):
        try:
            self.id = jsonData["id"]
            self.name =  localedTextDic[jsonData["name"]]
            self.shortDescription = localedTextDic[jsonData["shortDescription"]]
            self.imageUrl = jsonData["imageUrl"]
            self.color = jsonData["color"]
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load motivation data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJSON(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        jsonObject = json.loads (motivationDataJSON)

        return jsonObject

