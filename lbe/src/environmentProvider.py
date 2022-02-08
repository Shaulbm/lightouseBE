import datetime
import os
from random import random
from singleton import Singleton
import json
import random

ENVIRONMENT_FILE_PATH = "c:/dev/data/env/env.json"

def getAttribute(className, keyName):
    return EnvironmentProvider.getInstance().getAttribute(className,keyName)

def shouldSuppressNotifications ():
    if (EnvironmentProvider.getInstance().getAttribute(EnvKeys.behaviour, EnvKeys.supressMailNotifications) == 1):
        return True
    else:
        return False

def generateRandomUserColor():
    return EnvironmentProvider.getInstance().generateRandomUserColor()

class EnvKeys:
    courier = "courier"
    courierAuthToken = "token"
    defaults = "defaults"
    initialUserPassword = "initialUserPassword" 
    behaviour = "behaviour"
    moovs = "moovs"
    supressMailNotifications = "supressMailNotifications"
    hoursToNotifyBeforMoovsOverdue = "hoursToNotifyMoversOverDue"
    daysToAccomplishActiveMoov = "daysToAccomplishActiveMoov"
    seperationQuestionsScale = "seperationQuestionsScale"
    priorityMultiplayer = "priorityMultiplayer" 
    baseMoovPriority = "baseMoovPriority"
    baseMoovScore = "baseMoovScore"
    motivationGapBase = "motivationGapBase"
    topMoovThreshold = "topMoovThreshold"
    topRecommendedMoovThreshold = "topRecommendedMoovThreshold"
    recommendedMoovsIssueId = "recommendedMoovsIssueId"
    topRecommendedMoovsNo = "topRecommendedMoovsNo"
    relationshipDataTTLDays = "relationshipDataTTLDays"

class EnvironmentProvider (metaclass=Singleton):
    __instance__ = None
    userColors = ['#3D59E9','#607D8B', '#E91E63', '#FA982B', '#673AB7', '#F44336', '#4CAF50', '#3F50B5', '#8BC34A', '#2CA9F5', '#795548', '#CDDC39']

    def __init__(self):
        self.modificationTimeStamp = 0.0

    def getInstance():
        if EnvironmentProvider.__instance__ is None:
            EnvironmentProvider.__instance__ = EnvironmentProvider()

        return EnvironmentProvider.__instance__

    def invalidateValues(self):

        fileModifyTimestamp = os.path.getmtime(ENVIRONMENT_FILE_PATH)

        if (fileModifyTimestamp != self.modificationTimeStamp):
            environment_file = open(ENVIRONMENT_FILE_PATH)
            self.environmentValues = json.load (environment_file)
            self.modificationTimeStamp = fileModifyTimestamp

    def getAttribute(self, className, keyName):
        self.invalidateValues()
        return self.environmentValues[className][keyName] 

    def generateRandomUserColor(self):
        colorIdx = random.randint(0, len(self.userColors)-1)
        return self.userColors[colorIdx]

