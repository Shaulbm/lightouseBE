from re import A
import main
import gateway
import time
import uuid
from mongoDB import moovDBInstance
from generalData import QuestionData

main.startup()
'''
stocks.register_stock("MSFT")

index = 5

while index > 0:
    result = ""
    try:
        result = stocks.read_default()
    except Exception as e:
        print (e)

    print (result)
    time.sleep(5)
    index -= 1
'''
#stocks.register_user('Test4')
#stocks.create_training_data()
#stocks.get_course_lesson('ee728c15-c04a-4ecf-9c19-2a07ed37b65a', '1')
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

dbgId = "Q999" + "_" + str(uuid.uuid4())[:8] + "_10"
print ("dbgId is {0}", dbgId)

if "Q999" in dbgId:
    actualCurrQuestionId = dbgId[:dbgId.rfind('_')]
    print ("actual is {0}",actualCurrQuestionId)
