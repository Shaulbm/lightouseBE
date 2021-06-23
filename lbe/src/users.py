from threading import current_thread
from tinydb import TinyDB, Query
import uuid
from singleton import Singleton
import json

class UserData:
    def __init__(self, id = None, name  = None, mail = None, status = None, currentIssue = None, trainingStage = None, courseLesson = None, userDetails = None):
        if (userDetails is None):
            self.id = id
            self.name = name
            self.mail = mail
            self.status = status
            self.currentIssue = currentIssue
            self.trainingStage = trainingStage
            self.courseLesson = courseLesson
        else:
            # parse from json

            # mandatory fields
            self.id = userDetails[0]['id']
            self.name = userDetails[0]['name']

            # non mandatory fields - set default values:
            self.mail = ''
            self.status = ''
            self.currentIssue = ''
            self.trainingStage = ''


            # non mandatory values - set only if existing
            if ('mail' in userDetails[0]):
                self.mail = userDetails[0]['mail']

            if ('status' in userDetails[0]):
                self.status = userDetails[0]['status']

            if ('currentIssue' in userDetails[0]):    
                self.currentIssue = userDetails[0]['currentIssue']
            
            if ('trainingStage' in userDetails[0]): 
                self.trainingStage = userDetails[0]['trainingStage']

            if ('courseLesson' in userDetails[0]):
                self.courseLesson = userDetails[0]['courseLesson']

class trainingStageData:
    def __init__(self, id = None, trainingId  = None, challengeNumber = None, shortDescription = None, descriptionInDetails = None, trainingStageDetails = None):
        if (trainingStageDetails is None):
            self.id = id
            self.trainingId = trainingId
            self.challengeNumber = challengeNumber
            self.shortDescription = shortDescription
            self.descriptionInDetails = descriptionInDetails

        else:
            # parse from json

            # mandatory fields
            self.id = trainingStageDetails[0]['id']
            self.trainingId = trainingStageDetails[0]['trainingId']
            self.challengeNumber = trainingStageDetails[0]['challengeNumber']

            # non mandatory fields - set default values:
            self.shortDescription = ''
            self.descriptionInDetails = ''

            # non mandatory values - set only if existing
            if ('shortDescription' in trainingStageDetails[0]):
                self.shortDescription = trainingStageDetails[0]['shortDescription']

            if ('descriptionInDetails' in trainingStageDetails[0]):    
                self.descriptionInDetails = trainingStageDetails[0]['descriptionInDetails']

class trainingData:
    def __init__(self, id = None, name  = None, description = None, issueId = None, challengesNo = None, trainingDetails = None):
        if (trainingDetails is None):
            self.id = id
            self.name = name
            self.description = description,
            self.issueId = issueId
            self.callengesNo = challengesNo

        else:
            # parse from json

            # mandatory fields
            self.id = trainingDetails[0]['id']
            self.name = trainingDetails[0]['name']
            self.issueId = trainingDetails[0]['issueId']

            # non mandatory fields - set default values:
            self.description = ''
            self.challengesNo = ''

            # non mandatory values - set only if existing
            if ('description' in trainingDetails[0]):
                self.description = trainingDetails[0]['description']

            if ('challengesNumber' in trainingDetails[0]):
                self.challengesNo = trainingDetails[0]['challengesNumber']

class courseLessonData:
    def __init__(self, id = None, courseId  = None, lessonNumber = None, shortDescription = None, videoURL = None, courseLessonDetails = None):
        if (courseLessonDetails is None):
            self.id = id
            self.courseId = courseId
            self.lessonNumber = lessonNumber
            self.shortDescription = shortDescription
            self.videoURL = videoURL

        else:
            # parse from json

            # mandatory fields
            self.id = courseLessonDetails[0]['id']
            self.courseId = courseLessonDetails[0]['courseId']
            self.lessonNumber = courseLessonDetails[0]['lessonNumber']

            # non mandatory fields - set default values:
            self.shortDescription = ''
            self.videoURL = ''

            # non mandatory values - set only if existing
            if ('shortDescription' in courseLessonDetails[0]):
                self.shortDescription = courseLessonDetails[0]['shortDescription']

            if ('videoURL' in courseLessonDetails[0]):    
                self.videoURL = courseLessonDetails[0]['videoURL']


class courseData:
    def __init__(self, id = None, name  = None, description = None, issueId = None, partsNumber = None, courseDetails = None):
        if (courseDetails is None):
            self.id = id
            self.name = name
            self.description = description,
            self.issueId = issueId
            self.partsNumber = partsNumber

        else:
            # parse from json

            # mandatory fields
            self.id = courseDetails[0]['id']
            self.name = courseDetails[0]['name']
            self.issueId = courseDetails[0]['issueId']

            # non mandatory fields - set default values:
            self.description = ''
            self.partsNumber = ''

            # non mandatory values - set only if existing
            if ('description' in courseDetails[0]):
                self.description = courseDetails[0]['description']

            if ('partsNumber' in courseDetails[0]):
                self.partsNumber = courseDetails[0]['partsNumber']



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
                                    status = 'new', currentIssue = '', 
                                    trainingStage = '')
            self.insert_new_user(userDetails)
        else:
            # user found 
            userDetails = UserData (userDetails = foundUser)

        return userDetails

    def insert_new_user (self, userDetails):
        self.db.insert ({'id': userDetails.id ,'name': userDetails.name, 'mail': userDetails.mail, 'status': userDetails.status, 'currentTraining': userDetails.currentTraining, 'trainingStage' : userDetails.trainingStage})

    def createTrainingData (self):
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
            'shortDescription' : 'This is a short descritption for the first lesson',
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
            trainingStageDetails = trainingStageData (trainingStageDetails = foundTraingStageDetails)

        return trainingStageDetails

    def getTrainingData (self, issueId):
        trainingQuery = Query()
        trainingTable = self.db.table('trainingMetaData')
        foundTrainingDetails = trainingTable.search(trainingQuery.issueId == issueId)

        trainingDetails = None

        if (len(foundTrainingDetails) > 0):
            trainingDetails = trainingData (trainingDetails = foundTrainingDetails)

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
            courseLessonDetails = courseLessonData (courseLessonDetails = foundCourseLessonDetails)

        return courseLessonDetails


    def getCourseData (self, issueId):
        courseQuery = Query()
        coursesTable = self.db.table('courseMetaDataTable')
        foundCourseDetails = coursesTable.search(courseQuery.issueId == issueId)

        courseDetails = None

        if (len(foundCourseDetails) > 0):
            courseDetails = courseData (courseDetails = foundCourseDetails)

        return courseDetails


class   UsersLogic(metaclass=Singleton):
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

    