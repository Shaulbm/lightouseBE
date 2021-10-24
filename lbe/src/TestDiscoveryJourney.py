# import sys
# sys.path.insert(0, 'C:\Dev\LighthouseBE\lbe\src')

import gateway
from generalData import UserData

TESTS_NUMBER = 1

class questionsSetData:
    def __init__(self):
        self.id = ""
        self.questionsCount = 0
        self.questions = []

def main():
    
    currTest = 0
    while currTest < TESTS_NUMBER:
        #1. insert new user
        TestPrefix = "T_" + str(uuid.uuid4())[:8] 
        userId = TestPrefix + "_U_" + str(currTest)
        userMail = userId + "@gmail.com"
        gateway.add_or_update_user(userId, userMail)
        
        #2. start journey
        gateway.start_user_journey(userId)
        
        #3. get next batch
        questionBatch = gateway.get_next_questions_batch(userId, 1) 
        
        questionsSetDict = {}

        #4. while next batch is not empty

        while len(questionBatch) > 0:
            # organize questions in sets
            for currQuestion in questionBatch:
                if currQuestion.setId in questionsSetDict:
                    questionsSetDict[currQuestion.setId].questions.append(currQuestion)
                    questionsSetDict[currQuestion.setId].questionsCount += 1
                else:
                    newSetData = questionsSetData()
                    newSetData.id = currQuestion.setId
                    newSetData.questionsCount = 1
                    newSetData.questions.append (currQuestion)
                    questionsSetDict[currQuestion.setId] = newSetData

            for 
            questionBatch = gateway.get_next_questions_batch(userId, 1)
            #go over the questions and repond for each set 
            #notice if this is a special question - respond differently (select the number of responses required)
            pass

if __name__ == '__main__':
    main()