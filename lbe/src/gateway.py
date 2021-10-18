from fastapi import Header, APIRouter
from fastapi import HTTPException
from users import UsersLogic
from mongoDB import moovDBInstance

router = APIRouter()
users = UsersLogic()

@router.get("/motivation")
def get_motivation(id, locale):
    dbActions = moovDBInstance()
    motivationDetails = dbActions.getMotivation (id,int(locale))

    return motivationDetails

@router.get("/user")
def get_user(id, mail):
    dbActions = moovDBInstance()
    userDetails = dbActions.getUser (id, mail)

    return userDetails

@router.post("/setMotivations")
def set_motivations_to_user(id, motivations):
    dbActions = moovDBInstance()
    userDetails = dbActions.setMotivationsToUSer (id, motivations)

    return userDetails
    
# @router.post("/registerUser")
# def register_user(user):
#     userDetails = users.registerUser(userName=user)
#     return userDetails

# @router.get("/createTrainingData")
# def create_training_data():
#     return None #do nothing
#     users.createTrainingData()
    
# @router.post("/getTrainingStage")
# def get_training_stage(issueId, stage):
#     trainingStageDetails = users.getTrainingStage(issueId, stage)
#     return trainingStageDetails

# @router.post("/getCourseLesson")
# def get_course_lesson(issueId, lesson):
#     courselessonDetails = users.getCourseLessonData(issueId, lesson)
#     return courselessonDetails

# @router.post("/issue")
# def get_issue(id):
#     issueDetails = users.getIssueData(id)
#     return issueDetails

# @router.post("/trainingMap")
# def get_training_map(issueId, stage):
#     trainingMapDetails = users.getTrainingMap(issueId, stage)
#     return trainingMapDetails

# @router.post("/setUserIssueId")
# def set_user_issue_id(userName, issueId):
#     userDetails = users.setUserCurrIssueId(userName, issueId)
#     return userDetails

# @router.post("/setUserNextTrainingStage")
# def set_user_next_training_stage(userName):
#     userDetails = users.setUserNextTrainingStage(userName)
#     return userDetails

# @router.post("/setUserNextCourseLesson")
# def set_user_next_course_lesson(userName):
#     userDetails = users.setUserNextCourseLesson(userName)
#     return userDetails

# @router.post("/additionalIssueDetails")
# def additional_issue_details(issueId):
#     additionalIssueDetails = users.getIssueAdditionalData(issueId)
#     return additionalIssueDetails

# @router.post("/questionDetails")
# def question_details(questionId):
#     questionDetails = users.getQuestionDetails(questionId)
#     return questionDetails

# @router.post("/respondQuestion")
# def question_response(questionId, userId, response):
#     questionDetails = users.respondQuestion(questionId, userId, response)
#     return questionDetails

# @router.post("/userManager")
# def get_manager_details(userName):
#     managerDetails = users.getManagerDetails(name = userName)
#     return managerDetails

# @router.post("/usersUnder")
# def get_users_under(userName):
#     usersList = users.getUsersUnder(userName)
#     return usersList