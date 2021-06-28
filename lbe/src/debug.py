import main
import stocks
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
stocks.get_training_map('ee728c15-c04a-4ecf-9c19-2a07ed37b65a', '4')