import main
import gateway
import time

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
#gateway.question_details("35270681-08ec-44a5-b469-9ee8cf97bd31")
#userDetails = gateway.register_user("shaul.ben.maor@gmail.com")
managerDetails = gateway.get_manager_details('shaul.ben.maor@gmail.com')