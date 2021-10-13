from generalData import localedText
from collections import namedtuple
from bson import json_util
import json
import jsonpickle

def motivationDecoder (motivationDict):
    return namedtuple('X', motivationDict.keys())(*motivationDict.values())


class motivationData:
    def __init__(self):
        self._id = ""
        self.name = localedText()
        self.shortDescription = localedText()
        self.longDescription = localedText()
        self.additionalData = localedText()
        self.imageUrl = ""
        self.tailResolution = localedText()

    def fromJson (self, jsonData):
        # jsonDataStr = json_util.dumps(jsonData)
        # print (jsonDataStr)
        # motivtionObj = json.loads(jsonDataStr, object_hook=motivationDecoder)

        try:
            self._id = jsonData["_id"]
            self.name.en =  localedText(engText = jsonData["name"]["en"], hebText=jsonData["name"]["he"])
            self.shortDescription = localedText(engText = jsonData["shortDescription"]["en"], hebText=jsonData["shortDescription"]["he"])
            self.longDescription.en =localedText(engText = jsonData["longDescription"]["en"], hebText=jsonData["longDescription"]["he"])
            self.additionalData.en = localedText(engText = jsonData["additionalData"]["en"], hebText=jsonData["additionalData"]["he"])
            self.imageUrl = jsonData["imageUrl"]
            self.tailResolution.en = localedText(engText = jsonData["tailResolution"]["en"], hebText=jsonData["tailResolution"]["he"])
        except Exception as err:
            #log this
            raise TypeError(str.format("failed to load motivation data from JSON, data is {0}, error is {1}", jsonData, err))
       
        return

    def toJson(self):
        motivationDataJSON = jsonpickle.encode(self, unpicklable=False)

        return json.loads (motivationDataJSON)
