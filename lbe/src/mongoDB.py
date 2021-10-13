from pymongo import MongoClient
import pymongo
import json
from motivationsData import motivationData

def getDatabase():
    connectionString = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
    client = MongoClient(connectionString)

    return client.moov

def insertMotivation():
    db = getDatabase()
    motivationsCollection = db["motivationsTest"]

    newMotivation = motivationData()
    newMotivation._id = "M01"
    newMotivation.name.en = "Autonomy"
    newMotivation.name.he = "אוטונומיה"
    newMotivation.shortDescription.en = "english short description here"
    newMotivation.shortDescription.he = "חייב להיות לך מרחב להחליט ולפעול בדרך שבחרת, ושאחרים לא יתערבו ולא יכתיבו לך מה ואיך לעשות."

    motivationsCollection.insert_one (newMotivation.toJson())

def getMotivation (id):
    db = getDatabase()
    motivationCollection = db["motivationsTest"]

    motivationDataJSON = motivationCollection.find_one({"_id" : id})
    print ("motivation data is {0}", motivationDataJSON)

    newMotivtion = motivationData()
    newMotivtion.fromJson(motivationDataJSON)

    print ("motivation object is {0}", newMotivtion)

#insertMotivation()
getMotivation("M01")
