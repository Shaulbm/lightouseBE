from threading import current_thread
from tinydb import TinyDB, Query
import uuid
from singleton import Singleton
import json

class UserData:
    def __init__(self, id = None, name  = None, mail = None, status = None, currentTraining = None, trainingStage = None, userDetails = None):
        if (userDetails is None):
            self.id = id
            self.name = name
            self.mail = mail
            self.status = status
            self.currentTraining = currentTraining
            self.trainingStage = trainingStage
        else:
            # parse from json

            # mandatory fields
            self.id = userDetails[0]['id']
            self.name = userDetails[0]['name']

            # non mandatory fields - set default values:
            self.mail = ''
            self.status = ''
            self.currentTraining = ''
            self.trainingStage = ''

            # non mandatory values - set only if existing
            if ('mail' in userDetails[0]):
                self.mail = userDetails[0]['mail']

            if ('status' in userDetails[0]):
                self.status = userDetails[0]['status']

            if ('currentTraining' in userDetails[0]):    
                self.currentTraining = userDetails[0]['currentTraining']
            
            if ('trainingStage' in userDetails[0]): 
                self.trainingStage = userDetails[0]['trainingStage']

class usersDB:
    db_file:str
    def __init__(self, dbFilePath):
        self.db_file = dbFilePath
        self.db = TinyDB(self.db_file)
    
    def verify_user_exists (self, userName, userMail):
        userId = ""
        user = Query()

        foundUser = self.db.search (user.name == userName)

        if (len(foundUser) == 0):
           # no user with this name exists - add user  
            userId = str(uuid.uuid4())
            userDetails = UserData (id = userId, 
                                    name = userName, 
                                    mail = userMail, 
                                    status = 'new', currentTraining = '', 
                                    trainingStage = '')
            self.insert_new_user(userDetails)
        else:
            # user found 
            userDetails = UserData (userDetails = foundUser)

        return userDetails

    def insert_new_user (self, userDetails):
        self.db.insert ({'id': userDetails.id ,'name': userDetails.name, 'mail': userDetails.mail, 'status': userDetails.status, 'currentTraining': userDetails.currentTraining, 'trainingStage' : userDetails.trainingStage})


class UsersLogic(metaclass=Singleton):
    def __init__(self) -> None:
        self.usersDB = usersDB('c:\\dev\\lighthouseBE\\Data\\DB.json')
        pass

    def registerUser (self, userName):
        userDetails = self.usersDB.verify_user_exists(userName=userName, userMail='abc@gmail.com')
        return userDetails

    