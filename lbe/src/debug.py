from re import A
import main
import gateway
import time
import uuid
from mongoDB import moovDBInstance
import ExportJourney
from generalData import UserRoles, Locale, Gender, UserImageData
from os import path
import base64

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

# dbInstance.setMotivationsToUSer(id="U002", motivations=userMotivations)
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

def createUsers():
    #               U001
    #       UA02           UA03         UA04
    # UA05 UA06 UA07    UA08 UA09
    #
    #      UA10
    #   UA11 UA12
    # UA01 - HR
    gateway.add_or_update_user(id="U001", parentId= "" ,firstName="Shaul", familyName="Ben Maor", gender=Gender.MALE, locale=Locale.LOCALE_HEB_MA, orgId="O001", role=UserRoles.MANAGER, mailAddress="shaul@hotmail.com", personsOfInterest=["UA11", "UA12"])
    gateway.add_or_update_user(id="UA01", parentId= "" ,firstName="Debbi", familyName="Cohen", gender=Gender.FEMALE, locale=Locale.LOCALE_HEB_FE, orgId="O001", role=UserRoles.HR, mailAddress="")
    gateway.add_or_update_user(id="UA02", parentId= "U001" ,firstName="Rebbeca", familyName="Doe", gender=Gender.FEMALE, locale=Locale.LOCALE_EN, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA03", parentId= "U001" ,firstName="Jona", familyName="Kinklaid", gender=Gender.MALE, locale=Locale.LOCALE_EN, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA04", parentId= "U001" ,firstName="Riki", familyName="Class", gender=Gender.FEMALE, locale=Locale.LOCALE_HEB_FE, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA05", parentId= "UA02" ,firstName="Alex", familyName="Tatarski", gender=Gender.MALE, locale=Locale.LOCALE_HEB_MA, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA06", parentId= "UA02" ,firstName="Bessi", familyName="Dean", gender=Gender.FEMALE, locale=Locale.LOCALE_EN, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA07", parentId= "UA02" ,firstName="Sean", familyName="Major", gender=Gender.MALE, locale=Locale.LOCALE_EN, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA08", parentId= "UA03" ,firstName="Rex", familyName="Kruger", gender=Gender.MALE, locale=Locale.LOCALE_EN, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA09", parentId= "UA03" ,firstName="Mark", familyName="Zukerberg", gender=Gender.MALE, locale=Locale.LOCALE_HEB_MA, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA10", parentId= "" ,firstName="Shimshon", familyName="Levi", gender=Gender.MALE, locale=Locale.LOCALE_HEB_MA, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA11", parentId= "UA10" ,firstName="Shani", familyName="Cohen", gender=Gender.FEMALE, locale=Locale.LOCALE_HEB_FE, orgId="O001", role=UserRoles.MANAGER, mailAddress="")
    gateway.add_or_update_user(id="UA12", parentId= "UA10" ,firstName="Raz", familyName="Birenbaum", gender=Gender.MALE, locale=Locale.LOCALE_HEB_MA, orgId="O001", role=UserRoles.MANAGER, mailAddress="")

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
dbInstance = moovDBInstance()
# dbInstance.setMotivationsToUSer ("UA06", {"M001":3.5, "M002": 3.3, "M013": 3.1, "M014": 2, "M023": 1.7})
# motivations = dbInstance.getUserMotivations("U001", 1)
# print (motivations)
# userDetails = gateway.user_log_in("U001", "VVV")
# print (userDetails)
# foundSubjects = gateway.get_all_subjects(1)
# issue = gateway.get_issue_for_user('IS001', 'UA06', 1)
# print (issue)

moovDetails = gateway.get_moov("MO0001", 1)
print (moovDetails)

possibleMoovs = gateway.get_moovs_for_issue_and_user ("IS001", "UA06", 1)
print (possibleMoovs)