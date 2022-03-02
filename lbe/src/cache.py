import datetime
import threading
from common.rwLock import RWLock
from generalData import UserContextData, UserData
from motivationsData import MotivationData
from moovDB import MoovDBInstance

TTL_M = 720 
class BaseCacheItem:
    def __init__(self):
        self.timeStamp = datetime.datetime.now()

class User (BaseCacheItem):
    def __init__(self, motivationDetails : MotivationData):
        super().__init__()
        self.motivationDetails = motivationDetails

class UserDetailsCacheData (BaseCacheItem):
    def __init__(self, userDetails : UserData):
        super().__init__()
        self.userDetails = userDetails

class Cache:
    def __init__(self, db : MoovDBInstance):
        self.motivationsCache = {}
        self.usersCache = {}
        self.db = db
        self.motivationsLock = RWLock()
        self.usersLock = RWLock()

    # setting a unique id for ID + Locale + Gender 
    def getComplexId (self, id, userContext: UserContextData):
        complexId = id + '_L_'+ str(userContext.locale) + '_G_' + str(userContext.gender)

        return complexId  

    def getMotivationDetailsById(self, motivationId, userContext: UserContextData):
        motivationDetails = None
        motivationComplexId = self.getComplexId(id=motivationId, userContext=userContext)
        self.motivationsLock.reader_acquire()
        
        foundMotivationCacheDetails = None
        try: 
            if (motivationComplexId in self.motivationsCache):
                foundMotivationCacheDetails = self.motivationsCache[motivationComplexId]
        finally:
            self.motivationsLock.reader_release()

        if foundMotivationCacheDetails is not None:
            # verify TTL 
            if (datetime.datetime.utcnow() - foundMotivationCacheDetails.timeStamp) > datetime.timedelta(minutes=TTL_M):
                # TTL was breached, the data is no longer relevant.
                self.motivationsLock.writer_acquire()
                try:
                    self.motivationsCache.pop(motivationComplexId)
                finally:
                    self.motivationsLock.writer_release()
            else:
                # we found the motivation in the cache and its TTL is valid
                motivationDetails = foundMotivationCacheDetails.motivationDetails
    
        if motivationDetails is None:
            # no motivation data was found (or it was not valid) - create a cache entry
            motivationDetails = self.db.getMotivation(motivationId, userContext)
            motivationCacheData = User(motivationDetails)

            self.motivationsLock.writer_acquire()
            try:
                self.motivationsCache[motivationComplexId] = motivationCacheData
            finally:
                self.motivationsLock.writer_release()

        return motivationDetails

    def getUSerDetailsById(self, userId):
        userDetails = None
        self.usersLock.reader_acquire()
        
        foundUserCacheDetails = None
        try: 
            if (userId in self.usersCache):
                foundUserCacheDetails = self.usersCache[userId]
        finally:
            self.usersLock.reader_release()

        if foundUserCacheDetails is not None:
            # verify TTL 
            if (datetime.datetime.utcnow() - foundUserCacheDetails.timeStamp) > datetime.timedelta(minutes=TTL_M):
                # TTL was breached, the data is no longer relevant.
                self.usersLock.writer_acquire()
                try:
                    self.usersCache.pop(userId)
                finally:
                    self.usersLock.writer_release()
            else:
                # we found the user in the cache and its TTL is valid
                userDetails = foundUserCacheDetails.userDetails
    
        if userDetails is None:
            # no user data was found (or it was not valid) - create a cache entry
            userDetails = self.db.getUser(id=userId)
            userCacheData = UserDetailsCacheData(userDetails)

            self.usersLock.writer_acquire()
            try:
                self.usersCache[userId] = userCacheData
            finally:
                self.usersLock.writer_release()

        return userDetails

    # basically - for now, just remove from cache
    def setUserDirty(self, userId):

        self.usersLock.reader_acquire()  
        foundUserCacheDetails = None
        try: 
            if (userId in self.usersCache):
                foundUserCacheDetails = self.usersCache[userId]
        finally:
            self.usersLock.reader_release()

        if foundUserCacheDetails is not None:
            # found user in cache - remove it
            self.usersLock.writer_acquire()
            try:
                self.usersCache.pop(userId)
            finally:
                self.usersLock.writer_release()
    