from fastapi import Header, APIRouter
from fastapi import HTTPException
from users import UsersLogic

router = APIRouter()
users = UsersLogic()

@router.post("/registerUser")
def register_user(user):
    userDetails = users.registerUser(userName=user)
    return userDetails

@router.get("/createTrainingData")
def create_training_data():
    users.createTrainingData()
    pass

@router.post("/getTrainingStage")
def get_training_stage(issueId, stage):
    trainingStageDetails = users.getTrainingStage(issueId, stage)
    return trainingStageDetails

@router.post("/getCourseLesson")
def get_course_lesson(issueId, lesson):
    courselessonDetails = users.getCourseLessonData(issueId, lesson)
    return courselessonDetails

@router.post("/issue")
def get_issue(id):
    issueDetails = users.getIssueData(id)
    return issueDetails

@router.post("/trainingMap")
def get_training_map(issueId, stage):
    trainingMapDetails = users.getTrainingMap(issueId, stage)
    return trainingMapDetails

@router.post("/setUserIssueId")
def set_user_issue_id(userName, issueId):
    userDetails = users.setUserCurrIssueId(userName, issueId)
    return userDetails

@router.post("/setUserNextTrainingStage")
def set_user_next_training_stage(userName):
    userDetails = users.setUserNextTrainingStage(userName)
    return userDetails

@router.post("/setUserNextCourseLesson")
def set_user_next_course_lesson(userName):
    userDetails = users.setUserNextCourseLesson(userName)
    return userDetails