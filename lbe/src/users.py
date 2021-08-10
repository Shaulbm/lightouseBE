#from Sheets_handler import sheets_handler_script
from threading import current_thread
import json
from types import SimpleNamespace
from tinydb import TinyDB, Query, where
import uuid
from singleton import Singleton
from objectsData import UserData, trainingStageData, courseLessonData, courseData, trainingMapData, trainingData, questionData, issueData, additionalInfoData

STEPS_FOR_STAGE_MAP = 2

class usersDB:
    db_file:str
    def __init__(self, dbFilePath):
        self.db_file = dbFilePath
        self.db = TinyDB(self.db_file)
    
    def verify_user_exists (self, userName, userMail):
        userId = ""
        user = Query()
        usersTable = self.db.table('usersTable')


        foundUser = usersTable.search (user.name == userName)

        if (len(foundUser) == 0):
           # no user with this name exists - add user  
            userId = str(uuid.uuid4())
            userDetails = UserData (id = userId, 
                                    name = userName, 
                                    mail = userMail, 
                                    status = 'new', currentIssue = '', 
                                    trainingStage = '')
            self.insert_user(userDetails)
        else:
            # user found 
            userDetails = UserData (userDetails = foundUser[0])

        return userDetails

    def insert_user (self, userDetails):
        usersTable = self.db.table ("usersTable")
        usersTable.insert ({'id': userDetails.id ,'name': userDetails.name, 'mail': userDetails.mail, 'status': userDetails.status, 'currentIssue' : userDetails.currentIssue, 'trainingStage': userDetails.trainingStage, 'courseLesson' : userDetails.courseLesson})

    def update_user (self, userDetails):
        usersTable = self.db.table('usersTable')

        usersTable.update ({'id': userDetails.id ,'name': userDetails.name, 'mail': userDetails.mail, 'status': userDetails.status, 'currentIssue' : userDetails.currentIssue, 'trainingStage': userDetails.trainingStage, 'courseLesson' : userDetails.courseLesson},
                        where ('id') == userDetails.id)

    def getQuestionDetails (self, questionId):
        questionQuery = Query()
        questionsTable = self.db.table('discoveryQuestionsTable')
        foundQuestionDetails = questionsTable.search (questionQuery.id == questionId)

        questionDetails = None

        if (len (foundQuestionDetails) > 0):
            questionDetails = questionData(questionDetails = foundQuestionDetails[0])
        
        return questionDetails

    def createTrainingData (self):
        #not required any longer, protecting against DB corruption
        return

        issuesTable = self.db.table ('issuesTable')
        issueId = str(uuid.uuid4())
        issuesTable.insert({
            'Id' : issueId,
            'name' : 'Feedback',
            'description' : 'The user have issues providing feedback to his subprdonates, his peers or to his managers'
        })


        trainingMetaDataTable = self.db.table('trainingMetaData')
        trainingDetailsTable = self.db.table('trainingDetailsTable')

        #add first Traingin
        trainingId = str(uuid.uuid4())
        trainingMetaDataTable.insert({
            'id' : trainingId,
            'issueId' : issueId,
            'name' : 'This is the training Name',
            'description' : 'This is the training description',
            'challengesNumber' : '10',
        })

        #add first Challenge
        trainingChallengeId = str(uuid.uuid4())
        trainingDetailsTable.insert({
            'id' : trainingChallengeId,
            'trainingId' : trainingId,
            'challengeNumber' : '1',
            'shortDescription' : 'This is a short description of the first challenge',
            'descriptionInDetails' : 'This is a long description of the first challenge. Lorem ipsum dolor sit amet. Aut sint eius ea quibusdam doloribus est aspernatur nostrum est eaque obcaecati et iste error. Vel unde delectus sed adipisci quidem non asperiores alias et totam laborum vel consequatur natus! Et architecto omnis id numquam sapiente sit perferendis ducimus'})

        #add second challenge
        trainingChallengeId = str(uuid.uuid4())
        trainingDetailsTable.insert({
            'id' : trainingChallengeId,
            'trainingId' : trainingId,
            'challengeNumber' : '2',
            'shortDescription' : 'This is a short description of the second challenge',
            'descriptionInDetails' : 'This is a long description of the second challenge. Lorem ipsum dolor sit amet. Aut sint eius ea quibusdam doloribus est aspernatur nostrum est eaque obcaecati et iste error. Vel unde delectus sed adipisci quidem non asperiores alias et totam laborum vel consequatur natus! Et architecto omnis id numquam sapiente sit perferendis ducimus'})

        courseMetaDataTable = self.db.table ('courseMetaDataTable')
        courseLerssonsTable = self.db.table ('courseClassesTable')

        #add first course
        courseId = str(uuid.uuid4())
        courseMetaDataTable.insert({
            'id' : courseId,
            'issueId' : issueId,
            'name' : 'course name',
            'description' : 'This is the course description',
            'partsNumber' : '12'     
        })

        lessonId = str(uuid.uuid4())
        courseLerssonsTable.insert ({
            'id' : lessonId,
            'courseId' : courseId,
            'lessonNumber' : '1',
            'shortDescription' : 'This is a short descritption for the first lesson',
            'videoURL' : 'https://www.youtube.com//watch?v=DuWAyhxCqQ4'
        })

        lessonId = str(uuid.uuid4())
        courseLerssonsTable.insert ({
            'id' : lessonId,
            'courseId' : courseId,
            'lessonNumber' : '2',
            'shortDescription' : 'This is a short descritption for the second lesson',
            'videoURL' : 'https://www.youtube.com/watch?v=suIAo0EYwOE'
        })

    def getTrainingStageData (self, issueId, stage):
        trainingDetails = self.getTrainingData(issueId)
        
        if (trainingDetails is None):
            return None

        stageQuery = Query()
        trainingStages = self.db.table('trainingDetailsTable')
        foundTraingStageDetails = trainingStages.search ((stageQuery.trainingId == trainingDetails.id) & (stageQuery.challengeNumber == stage))

        trainingStageDetails = None

        if (len (foundTraingStageDetails) > 0):
            trainingStageDetails = trainingStageData (trainingStageDetails = foundTraingStageDetails[0])

        return trainingStageDetails

    def getTrainingData (self, issueId):
        trainingQuery = Query()
        trainingTable = self.db.table('trainingMetaData')
        foundTrainingDetails = trainingTable.search(trainingQuery.issueId == issueId)

        trainingDetails = None

        if (len(foundTrainingDetails) > 0):
            trainingDetails = trainingData (trainingDetails = foundTrainingDetails[0])

        return trainingDetails

    def getCourseLessonData (self, issueId, lesson):
        courseDetails = self.getCourseData(issueId)
        
        if (courseDetails is None):
            return None

        lessonQuery = Query()
        coursesLessons = self.db.table('courseClassesTable')
        foundCourseLessonDetails = coursesLessons.search ((lessonQuery.courseId == courseDetails.id) & (lessonQuery.lessonNumber == lesson))

        courseLessonDetails = None

        if (len (foundCourseLessonDetails) > 0):
            courseLessonDetails = courseLessonData (courseLessonDetails = foundCourseLessonDetails[0])

        return courseLessonDetails


    def getCourseData (self, issueId):
        courseQuery = Query()
        coursesTable = self.db.table('courseMetaDataTable')
        foundCourseDetails = coursesTable.search(courseQuery.issueId == issueId)

        courseDetails = None

        if (len(foundCourseDetails) > 0):
            courseDetails = courseData (courseDetails = foundCourseDetails[0])

        return courseDetails

    def getTrainingMap (self, issueId, stageStr):
        currentTrainingData = self.getTrainingData (issueId)
        currentTrainingStageData = self.getTrainingStageData(issueId, stageStr)

        if (currentTrainingData is None or currentTrainingStageData is None):
            return None

        currentTrainingMapData = trainingMapData (currentTrainingStageData)

        currentStageNumber = int (stageStr)

        if (currentStageNumber > 1):
            #not the first Stage
            for currentStageOffset in range (STEPS_FOR_STAGE_MAP):
                if (currentStageNumber - currentStageOffset - 1) > 0:
                    #Stage exists
                    currentTrainingMapData.pastStages.append(self.getTrainingStageData(issueId, str(currentStageNumber - currentStageOffset - 1)))

        if (currentStageNumber < int (currentTrainingData.challengesNo)):
            #not the last stage
            for currentStageOffset in range (STEPS_FOR_STAGE_MAP):
                if (currentStageNumber + currentStageOffset + 1) <= int (currentTrainingData.challengesNo):
                    #stage exists
                    currentTrainingMapData.futureStages.append(self.getTrainingStageData(issueId, str(currentStageNumber + currentStageOffset + 1)))

        return currentTrainingMapData

    def getIssueData (self, id):
        issueQuery = Query()
        issuesTable = self.db.table('issuesTable')
        foundIssueDetails = issuesTable.search(issueQuery.id == id)

        issueDetails = None

        if (len(foundIssueDetails) > 0):
            issueDetails = issueData (issuseDetails = foundIssueDetails[0])

        return issueDetails

    
    def setUserCurrIssueId (self, userName, issueId):
        userDetails = self.getUserDetails(userName)

        if (userDetails):
            userDetails.currentIssue = issueId
            userDetails.courseLesson = "1"
            userDetails.trainingStage = "1"
            self.update_user (userDetails)
        
        return userDetails

    def setUserNextTrainingStage (self, userName):
        userDetails = self.getUserDetails(userName)

        if (userDetails):
            currentTrainingData = self.getTrainingData (userDetails.currentIssue)

            if (currentTrainingData):
                currentUserStage = int (userDetails.trainingStage)
                trainingStagesNumber = int (currentTrainingData.challengesNo)
                if (currentUserStage < trainingStagesNumber):
                    #current training stage is not the last one
                    userDetails.trainingStage = str (currentUserStage + 1)
                    self.update_user (userDetails)
        
        return userDetails

    def setUserNextCourseLesson (self, userName):
        userDetails = self.getUserDetails(userName)

        if (userDetails):
            currentCourseData = self.getCourseData (userDetails.currentIssue)

            if currentCourseData:
                currentUserLesson = int (userDetails.courseLesson)
                coursePartsNumber = int (currentCourseData.partsNumber)
                if (currentUserLesson < coursePartsNumber):
                    #current course lesson is not the last one
                    userDetails.courseLesson = str (currentUserLesson + 1)
                    self.update_user (userDetails)
        
        return userDetails

    def getUserDetails (self, Name):
        user = Query()

        usersTable = self.db.table('usersTable')
        foundUser = usersTable.search (user.name == Name)
        userDetails = None

        if (len(foundUser) > 0):
            # user found 
            userDetails = UserData (userDetails = foundUser[0])
        
        return userDetails

    def getAdditionalIssueData (self, issueId):
        additionalInfoQuery = Query()
        additionalInfoTable = self.db.table('issuesAdditionalInfoTable')
        foundAdditionalInfoDetailsList = additionalInfoTable.search(additionalInfoQuery.issueId == issueId)

        additionalInfoDetailsList = []

        if (len (foundAdditionalInfoDetailsList) > 0):
            # found additional issue data - parse and add each on to the additionalInfoDetailsList
            for currAdditionalInfoDetails in foundAdditionalInfoDetailsList:
                additionalInfoDetails = additionalInfoData(additionalInfoDetails=currAdditionalInfoDetails)
                additionalInfoDetailsList.append(additionalInfoDetails)

        return additionalInfoDetailsList

class UsersLogic(metaclass=Singleton):
    def __init__(self) -> None:
        self.usersDB = usersDB('c:\\dev\\lighthouseBE\\Data\\DB.json')
        pass

    def registerUser (self, userName):
        userDetails = self.usersDB.verify_user_exists(userName=userName, userMail='abc@gmail.com')
        return userDetails

    def createTrainingData(self):
        self.usersDB.createTrainingData()

    def getTrainingData(self, issueId):
        trainingDetails = self.usersDB.getTrainingData(issueId)
        pass

    def getTrainingStage (self, issueId, stage):
        trainingStageDetails = self.usersDB.getTrainingStageData(issueId, stage)
        return trainingStageDetails

    def getCourseData(self, issueId):
        courseDetails = self.usersDB.getCourseData(issueId)
        return courseDetails

    def getCourseLessonData (self, issueId, lesson):
        courseLessonDetails = self.usersDB.getCourseLessonData(issueId, lesson)
        return courseLessonDetails

    def getTrainingMap (self, issueId, currentStage):
        trainingMapDetails = self.usersDB.getTrainingMap(issueId, currentStage)
        return trainingMapDetails

    def getIssueData (self, issueId):
        issueDetails = self.usersDB.getIssueData (issueId)
        return issueDetails

    def getIssueAdditionalData (self, issueId):
        additionalIssueInfoDetails = self.usersDB.getAdditionalIssueData(issueId)
        return additionalIssueInfoDetails

    def setUserCurrIssueId (self, userName, issueId):
        userDetails = self.usersDB.setUserCurrIssueId(userName, issueId)
        return userDetails

    def setUserNextTrainingStage(self, userName):
        userDetails = self.usersDB.setUserNextTrainingStage(userName)
        return userDetails

    def setUserNextCourseLesson(self, userName):
        userDetalis = self.usersDB.setUserNextCourseLesson(userName)
        return userDetalis

    def getQuestionDetails (self, questionId):
        questionDetails = self.usersDB.getQuestionDetails (questionId)
        return questionDetails
