from threading import current_thread
from typing import Text
from pymongo import MongoClient
import pymongo
import json
from motivationsData import motivationData
from generalData import textData

LOCALE_HEB_MA = 1
LOCALE_HEB_FE = 2
LOCALE_EN = 3


def getDatabase():
    connectionString = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
    client = MongoClient(connectionString)

    return client.moov

def insertMotivation():
    db = getDatabase()
    motivationsCollection = db["motivationsTest"]

    heb_ma_LocaleCollection = db["locale_he_ma"]
    heb_fe_LocaleCollection = db["locale_he_fe"]
    eng_LocaleCollection = db["locale_en"]

    newMotivation = motivationData()
    newMotivation.id = "M01"
    newMotivation.name = "M01_1"
    newMotivation.shortDescription = "M01_2"
    newMotivation.longDescription = "M01_3"
    newMotivation.tailResolution = "M01_4"
    newMotivation.imageUrl = "url"

    currentTextData = textData("M01", "M01_1", "Autonomy")
    eng_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData("M01", "M01_1", "אוטונומיה")
    heb_ma_LocaleCollection.insert_one(currentTextData.toJson())
    heb_fe_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_2", "english short description here")
    eng_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_2", "חייב להיות לך מרחב להחליט ולפעול בדרך שבחרת, ושאחרים לא יתערבו ולא יכתיבו לך מה ואיך לעשות.")
    heb_ma_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_2","את צריכה לעשות את הדברים בדרך שלך, ומבלי שאחרים יתערבו וודאי מבלי שאחרים יכתיבו לך מה ואיך לעשות")
    heb_fe_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_3", "english long description here")
    eng_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_3", "אתה במיטבך כשיש לך מרחב להחליט ולפעול. אתה צריך לעשות את הדברים בדרך שלך, ומבלי שאחרים יתערבו וודאי מבלי שאחרים יכתיבו לך מה ואיך לעשות. חופש לפעול ועצמאות בקבלת ההחלטות הם הכרח עבורך. אתה לא אוהב לפעול על פי כללים ונהלים, ודאי לא אלה שלא אתה קבעת לעצמך. בכלל, קרוב לודאי שעבודה לבד מועדפת עלייך. זה כמובן לא אומר שאתה לא עובד או לא יכול לעבוד עם אחרים, אלא שכשהחלטות לא נמצאות באופן מלא בידיים שלך, אתה חש שאתה לא במיטבך.")
    heb_ma_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_3","את במיטבך כשיש לך מרחב להחליט ולפעול. את צריכה לעשות את הדברים בדרך שלך, ומבלי שאחרים יתערבו וודאי מבלי שאחרים יכתיבו לך מה ואיך לעשות. חופש לפעול ועצמאות בקבלת ההחלטות הם הכרח עבורך. את לא אוהבת לפעול על פי כללים ונהלים, ודאי לא אלה שלא את קבעת לעצמך. בכלל, קרוב לודאי שעבודה לבד מועדפת עלייך. זה כמובן לא אומר שאת לא עובדת או לא יכולה לעבוד עם אחרים, אלא שכשהחלטות לא נמצאות באופן מלא בידיים שלך, את חשה שאת לא במיטבך.")
    heb_fe_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_4", "autonnomy tail resolution phrase")
    eng_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_4", "ליצור איכות ולהימנע מבינוניות")
    heb_ma_LocaleCollection.insert_one(currentTextData.toJson())

    currentTextData = textData ("M01", "M01_4","ליצור איכות ולהימנע מבינוניות")
    heb_fe_LocaleCollection.insert_one(currentTextData.toJson())

    motivationsCollection.insert_one (newMotivation.toJson())

def getMotivation (id, locale):
    db = getDatabase()
    motivationCollection = db["motivationsTest"]

    motivationDataJSON = motivationCollection.find_one({"id" : id})
    print ("motivation data is {0}", motivationDataJSON)

    motivationTextsDic = getTextDataByParent(id, locale)

    newMotivtion = motivationData()
    newMotivtion.buildFromJson(motivationDataJSON, motivationTextsDic)

    print ("motivation object is {0}", newMotivtion)

def getTextDataByParent (parentId, locale):
    textDataCollection = getTextCollectionByLocale(locale)
        
    allTextsArray = textDataCollection.find ({"parentId" : parentId})

    textDic = {}

    for currText in allTextsArray:
        textDic[currText["textId"]] = currText["text"]

    return textDic

def getTextCollectionByLocale(locale):
    db = getDatabase()

    if locale == LOCALE_HEB_FE:
        return db["locale_he_fe"]
    elif locale == LOCALE_HEB_MA:
        return db["locale_he_ma"]
    elif locale == LOCALE_EN:
        return db["locale_en"]
    else:
        return db ["locale_en"]

#insertMotivation()
getMotivation("M01", LOCALE_HEB_MA)
