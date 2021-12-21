import datetime
import threading
from motivationsData import MotivationData
from mongoDB import moovDBInstance

TTL_M = 720

class BaseCacheData:
    def __init__(self):
        self.timeStamp = datetime.datetime.now()

class MotivationCacheData (BaseCacheData):
    def __init__(self, motivationData : MotivationData):
        super().__init__()
        self.motivationDetails = motivationData

class Cache:
    def __init__(self, db : moovDBInstance):
        self.motivations = {}
        self.db = db
        self.motivationsLock = threading.Lock()

    def getMotivationDetailsById(self, motivationId):
        self.motivationsLock.acquire()
        try:
            if (motivationId in self.motivations):
                if (datetime.datetime.utcnow() - self.motivations[motivationId].timeStamp) > datetime.timedelta(minutes=TTL_M):
                    # TTL was breached, the data is no longer relevant.
                    self.motivations.pop(motivationId)
                else:
                    return self.motivations[motivationId]

            # no motivation data was found (or it was deleted)
            
        finally:
            self.motivationsLock.release()