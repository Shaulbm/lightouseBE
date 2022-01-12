import datetime
import os
from singleton import Singleton
import json

ENVIRONMENT_FILE_PATH = "c:/dev/data/env/env.json"

def getAttribute(className, keyName):
    return EnvironmentProvider.getInstance().getAttribute(className,keyName)

def shouldSuppressNotifications ():
    if (EnvironmentProvider.getInstance().getAttribute(EnvKeys.behaviour, EnvKeys.supressMailNotifications) == 1):
        return True
    else:
        return False

class EnvKeys:
    courier = "courier"
    courierAuthToken = "token"
    defaults = "defaults"
    initialUserPassword = "initialUserPassword" 
    behaviour = "behaviour"
    supressMailNotifications = "supressMailNotifications"
    hoursToNotifyBeforMoovsOverdue = "hoursToNotifyMoversOverDue"
    daysToAccomplishActiveMoov = "daysToAccomplishActiveMoov"

class EnvironmentProvider (metaclass=Singleton):
    __instance__ = None

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

