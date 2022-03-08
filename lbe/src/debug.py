import datetime
from starlette.requests import Request
from starlette.types import Scope
from moovLogic import MoovLogic
import main
import gateway
import time
import uuid
from moovDB import MoovDBInstance
import ExportJourney
from generalData import UserRoles, Locale, Gender, UserImageData, UserData, UserContextData, UserRelationshipData
from os import path
import base64
import cache
import schedule
import environmentProvider as ep

#gateway.get_training_map('ee728c15-c04a-4ecf-9c19-2a07ed37b65a', '4')
#gateway.get_issue('ee728c15-c04a-4ecf-9c19-2a07ed37b65a')
#gateway.set_user_issue_id ('Test2', 'ee728c15-c04a-4ecf-9c19-2a07ed37b65a')
#gateway.set_user_next_training_stage('shaul.ben.maor@gmail.com')
#gateway.additional_issue_details('ee728c15-c04a-4ecf-9c19-2a07ed37b65a')
#gateway.question_details("b6a9a02d-534e-4259-ad1a-9833a125e5b4")
#userDetails = gateway.register_user("shaul.ben.maor@gmail.com")
#managerDetails = gateway.get_manager_details('shaul.ben.maor@gmail.com')
#gateway.get_users_under("boss@gmail.com")
#gateway.get_motivation("M002",2)

# userMotivations={"M002" : "7", "M004" : "12", "M006" : "19", "M008" : "8", "M010" : "12"}
# userMotivations={"M001" : "7", "M003" : "12", "M005" : "19", "M007" : "8", "M009" : "12"}

# newUser = userData (id = "U001", mailAddress="shaul@hotmail.com", motivations=userMotivations)
# dbInstance = moovDBInstance()
# dbInstance.insertOrUpdateUser(newUser)

#gateway.get_user(id="U001",mail="")

# newUser = QuestionData (id = "U002", mailAddress="smadar@hotmail.com")
# dbInstance = moovDBInstance()
# dbInstance.insertOrUpdateUser(newUser)

#gateway.get_user(id="U002", mail="")

# dbInstance.getQuestion("Q002", 2)

# gateway.start_user_journey(userId="U001")
# questions = gateway.get_next_questions_batch(userId="U001", locale=1)
# print (questions)
#gateway.set_journey_question_response(userId="U001", questionId="Q002", responseId="R006")

# dbgId = "Q999" + "_" + str(uuid.uuid4())[:8] + "_10"
# print ("dbgId is {0}", dbgId)

# if "Q999" in dbgId:
#     actualCurrQuestionId = dbgId[:dbgId.rfind('_')]
#     print ("actual is {0}",actualCurrQuestionId)

# jid = gateway.start_user_journey("U001")
# questionsList = gateway.get_next_questions_batch("U001", 1)
# print (questionsList)

# ExportJourney.writeJourneyTestReport([])


# A = "Q999_e9957af6"
 
# if "Q999" not in A:
#     print ("bla")
# else:
#     print ("blu")

# db = moovDBInstance()
# db.insertOrUpdateUserDetails(id="U001", mail = "shaul@hotmail.com", firstName = "Shaul", familyName = "Ben Maor", role = UserRoles.MANAGER)
# user = gateway.get_user("U001")
# print (user.toJSON())
# gateway.start_user_journey("U001")

# questionsList = gateway.get_next_questions_batch("U001", 1)
# print (questionsList)
# motivations = gateway.get_all_motivations(1)
# print (motivations)

def job():
    print ('in job, time is ', str(datetime.datetime.utcnow()))

def createUsers(dbInstance):
    #               U001
    #       UA02           UA03         UA04
    # UA05 UA06 UA07    UA08 UA09
    #
    #      UA10
    #   UA11 UA12
    # UA01 - HR
    dbInstance.insertOrUpdateUserDetails(id="U001", parentId= "" ,firstName="Shaul", familyName="Ben Maor", gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="U001@testUser.com", personsOfInterest=["UA11", "UA12"])
    dbInstance.insertOrUpdateUserDetails(id="UA01", parentId= "" ,firstName="Debbi", familyName="Cohen", gender=Gender.FEMALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.HR, mailAddress="UA01@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA02", parentId= "U001" ,firstName="Rebbeca", familyName="Doe", gender=Gender.FEMALE, locale=Locale.LOCALE_EN_US, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA02@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA03", parentId= "U001" ,firstName="Jona", familyName="Kinklaid", gender=Gender.MALE, locale=Locale.LOCALE_EN_US, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA03@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA04", parentId= "U001" ,firstName="Riki", familyName="Class", gender=Gender.FEMALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA04@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA05", parentId= "UA02" ,firstName="Alex", familyName="Tatarski", gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA05@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA06", parentId= "UA02" ,firstName="Bessi", familyName="Dean", gender=Gender.FEMALE, locale=Locale.LOCALE_EN_US, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA06@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA07", parentId= "UA02" ,firstName="Sean", familyName="Major", gender=Gender.MALE, locale=Locale.LOCALE_EN_US, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA07@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA08", parentId= "UA03" ,firstName="Rex", familyName="Kruger", gender=Gender.MALE, locale=Locale.LOCALE_EN_US, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA08@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA09", parentId= "UA03" ,firstName="Mark", familyName="Zukerberg", gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA09@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA10", parentId= "" ,firstName="Shimshon", familyName="Levi", gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA10@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA11", parentId= "UA10" ,firstName="Shani", familyName="Cohen", gender=Gender.FEMALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA11@testUser.com")
    dbInstance.insertOrUpdateUserDetails(id="UA12", parentId= "UA10" ,firstName="Raz", familyName="Birenbaum", gender=Gender.MALE, locale=Locale.LOCALE_HE_IL, orgId="O001", role=UserRoles.MANAGER, mailAddress="UA12@testUser.com")

    dbInstance.setUserPassword("U001", "123456")
    dbInstance.setUserPassword("UA01", "123456")
    dbInstance.setUserPassword("UA02", "123456")
    dbInstance.setUserPassword("UA03", "123456")
    dbInstance.setUserPassword("UA04", "123456")
    dbInstance.setUserPassword("UA05", "123456")
    dbInstance.setUserPassword("UA06", "123456")
    dbInstance.setUserPassword("UA07", "123456")
    dbInstance.setUserPassword("UA08", "123456")
    dbInstance.setUserPassword("UA09", "123456")
    dbInstance.setUserPassword("UA10", "123456")
    dbInstance.setUserPassword("UA11", "123456")
    dbInstance.setUserPassword("UA12", "123456")

# createUsers()

# usersCircle = gateway.get_user_circle("U001")
# print (usersCircle)

# motivationsList = gateway.get_all_motivations(1)
# print (motivationsList)

# journeyId = gateway.start_user_journey('U001')
# gateway.set_journey_question_response('U001', 'Q001', 'R001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')
# questionsList = gateway.get_next_questions_batch('U001')

# # gateway.get_issue(id="IS001", locale=Locale.UNKNOWN)
# dbInstance = moovDBInstance()
# # dbInstance.setMotivationsToUSer("U001", ['M001', 'M002', 'M003', 'M004', 'M005'])
# issueDetails = gateway.get_issue("IS001", Locale.LOCALE_HEB_FE)
# issueByUser = gateway.get_issue_for_user("IS001", "U001", Locale.LOCALE_HEB_FE)

#file_used = 'C:/Users/shaul/Downloads/Persons/F1.jfif'
# my_file = path(file_used)
# if my_file.is_file():
#     print("File Exists") #prints successfully

# with open(file_used, 'rb') as fout:
#     userImage = base64.b64encode(fout.read())
#     dbInstance = moovDBInstance()
#     imageData = UserImageData("U001", userImage)
#     dbInstance.insertOrUpdateUserImage(imageData)


# #Image - start
# dbInstance = moovDBInstance()
# newImageFile = 'c:/Temp/Images/U001.jfif'
# # userImageDetails = dbInstance.getUserImage("U001")

# file_used = 'C:/Users/shaul/Downloads/Persons/F1.jfif'
# # with open(file_used, 'rb') as fout:
# origFile = open(file_used, 'rb')

# # userImage = base64.b64encode(origFile.read())
# userImage = origFile.read()
# #     dbInstance = moovDBInstance()
# imageData = UserImageData("U001", userImage)
# dbInstance.insertOrUpdateUserImage(imageData)

# # ImageDecodedData = base64.b64decode(imageData.image['py/b64'])
# # ImageDecodedData = base64.b64decode(imageData.image)

# userImageDetails = dbInstance.getUserImage("U001")

# fout = open(newImageFile, 'wb')
# # fout.write(ImageDecodedData)
# fout.write(userImageDetails.image)
# # fout.write(struct.pack('>i', 42))
# # fout.write(struct.pack('>f', 2.71828182846))

# fout.close()
#Image - End
dbInstance_1 = MoovDBInstance()
# dbInstance.setMotivationsToUSer ("UA06", {"M001":3.5, "M002": 3.3, "M013": 3.1, "M014": 2, "M023": 1.7})
# motivations = dbInstance.getUserMotivations("U001", 1)
# print (motivations)
# userDetails = gateway.user_log_in("U001", "VVV")
# print (userDetails)
# foundSubjects = gateway.get_all_subjects(1)
# issue = gateway.get_issue_for_user('IS001', 'UA06', 1)
# print (issue)

# moovDetails = gateway.get_moov("MO0001", 1)
# print (moovDetails)

# possibleMoovs = gateway.get_moovs_for_issue_and_user ("IS001", "UA06", 1)
# print (possibleMoovs)

# activeMooveDetails = gateway.activate_moov("MO0001", "U001", "UA06")
# foundActiveMoobForCP = gateway.get_active_moovs_to_counterpart("U001","UA06", 1)
# foundActiveMoobForUser = gateway.get_active_moov_for_user("U001")
# gateway.end_moov(activeMooveDetails.id, 2, "no real feedback")
db = MoovLogic()

# usersCollection = db["users"]

# foundUsers = usersCollection.find()

# for currUserJSON in foundUsers:
#     currUserDetails = UserData()
#     currUserDetails.fromJSON(currUserJSON)

#     if (currUserDetails.mailAddress == ""):
#         currUserDetails.mailAddress = currUserDetails.id + "@testUser.com"

#         dbInstance_1.insertOrUpdateUser(currUserDetails)

# useCOI = dbInstance_1.getUserCircle("U001")

# userImage = gateway.get_user_image(userId = 'U001', request=None)

# dbInstance_1.setUserPassword("U001", "123456")
# userDetails = dbInstance_1.userLogin("UA01@testUser.com", "123456")

# userContext = UserContextData("U001", "Shaul", "Ben Maor", Gender.MALE, Locale.LOCALE_EN_US, isRTL=False)
# usersConflicts = dbInstance_1.getConflictsForUsers('UA06', 'UA08', False, userContext)
# scope = Scope()
# scope["type"] = "http"
# request = Request(scope=scope)
# request.headers["X-USER-ID"] = 'U001'
# usersConflicts = gateway.get_conflicts_for_users(request=None, userId="UA06", counterpartId="UA08", userContext=userContext)

# foundMoovs = dbInstance_1.getConflictMoovs(conflictId='CO003', userContext=userContext)
# foundMoovs = dbInstance_1.getMoovsForIssueAndUser(userId="UA06", issueId='IS001', userContext=userContext)

# activeMooveDetails = dbInstance_1.activateMoov(moovId="MO0001", userId="U001", counterpartId="UA06", userContext=userContext)
# foundActiveMoobForCP = gateway.get_active_moovs_to_counterpart("U001","UA06", 1)
# foundActiveMoobForUser = gateway.get_active_moov_for_user("U001")
# dbInstance_1.endMoov(activeMoovId='AM_1', feedbackScore=2, feedbackText="no real feedback")
# activeConflictMoov = dbInstance_1.activateConflictMoov(moovId='CMO0001', userId='U0001', counterpartsIds=['UA06', 'UA08'],userContext=userContext)

# userDetail = dbInstance_1.getUser(id='U001')
# createUsers(dbInstance_1)
# db.setMotivationsToUSer("U001", {"M001": {"motivationId" : "", "journeyScore" : 3.5, "gapFactor": 0}, 
#                                             "M001": {"motivationId" : "M001", "journeyScore" : 3.3, "gapFactor": -2}, 
#                                             "M002": {"motivationId" : "M002", "journeyScore" : 3.1, "gapFactor": -1}, 
#                                             "M003": {"motivationId" : "M003", "journeyScore" : 2, "gapFactor": 1}, 
#                                             "M004": {"motivationId" : "M004", "journeyScore" : 1.7, "gapFactor": 2},
#                                             "M005": {"motivationId" : "M004", "journeyScore" : 1.3, "gapFactor": 2}})

# db.setMotivationsToUSer("UA06", {"M001": {"motivationId" : "", "journeyScore" : 3.5, "gapFactor": 0}, 
#                                             "M001": {"motivationId" : "M001", "journeyScore" : 3.3, "gapFactor": -2}, 
#                                             "M002": {"motivationId" : "M002", "journeyScore" : 3.1, "gapFactor": -1}, 
#                                             "M013": {"motivationId" : "M013", "journeyScore" : 2, "gapFactor": 1}, 
#                                             "M014": {"motivationId" : "M014", "journeyScore" : 1.7, "gapFactor": 2},
#                                             "M023": {"motivationId" : "M023", "journeyScore" : 1.3, "gapFactor": 2}})

# db.setMotivationsToUSer("UA08", {"M001": {"motivationId" : "", "journeyScore" : 3.5, "gapFactor": 0}, 
#                                             "M023": {"motivationId" : "M023", "journeyScore" : 3.3, "gapFactor": -2}, 
#                                             "M028": {"motivationId" : "M028", "journeyScore" : 3.1, "gapFactor": -1}, 
#                                             "M021": {"motivationId" : "M021", "journeyScore" : 2, "gapFactor": 1}, 
#                                             "M007": {"motivationId" : "M007", "journeyScore" : 1.7, "gapFactor": 2},
#                                             "M011": {"motivationId" : "M011", "journeyScore" : 1.3, "gapFactor": 2}})# dbInstance_1.setMotivationsToUSer("UA08", {"M023" : 7, "M028" : "12", "M021" : "19", "M007" : "8", "M011" : "12"})
# dbInstance_1.setMotivationsToUSer("UA06", {"M001":3.5, "M002": 3.3, "M013": 3.1, "M014": 2, "M023": 1.7})
# userDetails = dbInstance_1.userLogin('U001@testUser.com', '123456')
# motivationDetails = dbInstance_1.getMotivation('M023', userContext)

# userContext = dbInstance_1.setUserContextData('U001')
# moovs= dbInstance_1.getConflictsMoovsForUsers('UA06', 'UA08', userContext=userContext)

# user = db.getUser('U001')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('UA01')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('U001')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('UA01')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('UA02')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('UA01')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('U001')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('UA03')
# print ('user id {0}, user name {1}', user.id, user.firstName)
# user = db.getUser('U001')
# print ('user id {0}, user name {1}', user.id, user.firstName)

# motivation = db.getMotivation('M001', userContext)
# motivation = db.getMotivation('M001', userContext)
# subjects = db.getAllSubjects(userContext)
# issues = db.getAllIssues(userContext)



# moovInstance = db.activateIssueMoov('MO0002', 'U001', 'UA06', userContext)
# moovInstances = db.getActiveMoovsToCounterpart('U001', 'UA06', userContext)
# jsonData = moovInstances[1].toJSON()

# foundMoovs = db.getAllMoovsPlannedToEnd(datetime.utcnow())
# users = db.getInterestedusers('UA11')

# newUser = UserData (id = "UT01", mailAddress="shaul.ben.maor@gmail.com", firstName= "john", familyName="doe", orgId="O003", locale=Locale.LOCALE_HE_IL)
# dbInstance = moovDBInstance()
# dbInstance.insertOrUpdateUser(newUser)
# db.insertOrUpdateUser(newUser)
# main.startup()
db.setUserContextData("U001")
# db.activateIssueMoov(moovId="MO0001", userId="U001", counterpartId="UA06", userContext=userContext)

# index = 0
# while True:
#     print ('iteration {}', index)
#     index += 1
#     time.sleep(3)

# issue = db.getIssueForCounterpart("IS001", "UA06", userContext=userContext)
# moovs = db.getMoovsForIssueAndCounterpart("UA06", "IS001", userContext)
# relationshipDetails = UserRelationshipData('U001', 'UA06', 3, 2)
# db.insertOrUpdateRelationship(relationshipDetails)
# activeMoov = db.activateIssueMoov('MO0002', 'U001', 'UA06', userContext=userContext)


# users = []
# users.append(db.getUser("U001"))
# users.append(db.getUser("UA01"))
# users.append(db.getUser("UA02"))
# users.append(db.getUser("UA03"))
# users.append(db.getUser("UA04"))
# users.append(db.getUser("UA05"))
# users.append(db.getUser("UA06"))
# users.append(db.getUser("UA07"))
# users.append(db.getUser("UA08"))
# users.append(db.getUser("UA09"))
# users.append(db.getUser("UA10"))
# users.append(db.getUser("UA11"))
# users.append(db.getUser("UA12"))

# for currUser in users:
#     currUser.color = ep.generateRandomUserColor()
#     db.insertOrUpdateUser(currUser)

# users = db.getUserCircle('U001')
# moovs = db.getTopRecommendedMoovsForCounterpart('U001', 'UA06', userContext)

# user: UserData = db.getUser('UA01')
# user.personsOfInterest = ['UA02']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA02')
# user.personsOfInterest = ['UA01','UA03']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA03')
# user.personsOfInterest = ['UA01','UA02','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA04')
# user.personsOfInterest = ['UA01','UA02','UA03','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA05')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA06')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA07')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA08')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA09')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA08','UA10']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA10')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA08','UA09','UA11']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('U001')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA08','UA09','UA10','UA12']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user: UserData = db.getUser('UA12')
# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA08','UA09','UA10','UA11','U001']
# user.parentId = ""
# db.insertOrUpdateUser(user)

# user.personsOfInterest = ['UA01','UA02','UA03','UA04','UA05','UA06','UA07','UA08','UA09','UA10','UA11','UA12']

# coi = db.getUserCircle('UA02')

# moovInstances = db.getActiveMoovsToCounterpart('U001', 'UA06', userContext)
# MoovInstances = db.getActiveMoovsForUser('U001', userContext)

# activeMoov = db.getActiveMoov('AM_8')
# db.extendAcctiveMoov('AM_8', (datetime.datetime.utcnow() + datetime.timedelta(days=7)))
# newActiveMoov = db.getActiveMoov('AM_8')

# a = "•בקש מ<<>> שיספר לך מהי התדירות הנכונה לו לדווח על התקדמות/החלטות/תוצאות שלו. הבהר לו את חשיבות העדכונים. •סכמו יחד על מתכונת שתאפשר לך ולאחרים לחוש בנוח, ובו זמנית תגרום לו לחוש שלא יושבים לו על הצוואר. •הגדירו את ערוץ התקשורת (מייל/הודעה/פגישה/בע״פ), ש(יאפשר לו לבחור את הדרך המיטבית עבורו - להוריד) הנוח והטוב עבורו. חשוב שהערוץ שתבחרו ייתן מענה גם לצרכים הניהוליים שלך ושל הגורמים הרלוונטיים האחרים. •קבעו את תדירות הדיווח: מתי אתה וגורמים רלוונטיים אחרים צריכים לקבל את המידע אודות התקדמות המשימה (האם נדרש דיווח במהלך הביצוע או ניתן להסתפק בעדכון על השלמת ביצוע?).•דגלים אדומים: הגדירו מתי ובאילו נסיבות נדרש להתריע על בעיה. קבעו באיזה צורות תעשה ההתרעה (אימייל? ווטסאפ? שיחת פנים אל פנים? וכד')."
# b = a.replace('•', '*')

# moovInstance=db.getPastMoovsToMoovAndCounterpart('U001', 'UA06', 'MO0091', userContext)
# activMoov = db.activateIssueMoov('MO0092', 'U001', 'UA06', userContext)
# moovPriority = db.calculateIssueMoovPriority ('U001', 'UA06', 'M001')

# db.updateUserDetails('U001', 'en-US', 1)
# db.updateUserPassword('U001', '654321', '123456')

# userContext = UserContextData("U001", "Shaul", "Ben Maor", Gender.MALE, Locale.LOCALE_HE_IL, isRTL=False)
userContext = db.getUserContextData('U001')
# moovs = db.getMoovsForIssueAndCounterpart('UA06', 'IS003', userContext=userContext)

# activeMoov = db.activateIssueMoov('MO0003', 'U001', 'UA06', userContext=userContext)
# db.endMoov('AM_9', 3, 'none', False)
# motivations = db.getAllMotivations(userContext=userContext)
# activeMoovs = db.getActiveMoovsForUser('U001', userContext=userContext)
# users = db.getUserCircle('U001')
# relationship = db.insertOrUpdateRelationshipDetails("U001", "UA03", 3, 5)
# db.insertOrUpdateRelationshipDetails('U001', 'UA07', 3, 5)
# result = db.missingRelationshipData('U001', 'UA07')
# res = db.sendUserFeedback('U001', "moov", "חסר לי משהו - אין לי מושג מה")

# motivation = db.getMotivation('M003', userContext=userContext)
activeMoovs = db.getActiveMoovsForUser('U001',userContext=userContext)
print ("Done")