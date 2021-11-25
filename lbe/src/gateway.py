from fastapi import Header, APIRouter
from fastapi import HTTPException
from pymongo.common import MIN_SUPPORTED_SERVER_VERSION
from mongoDB import moovDBInstance
import userDiscoveryJourney
from generalData import UserRoles, Gender, Locale
from loguru import logger
import ast
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    userId: str
    password: str

@router.get("/motivation")
def get_motivation(id, locale):
    dbActions = moovDBInstance()
    motivationDetails = dbActions.getMotivation (id,int(locale))

    return motivationDetails

@router.post("/login")
def user_log_in(loginData : LoginData):
    dbActions = moovDBInstance()
    userDetails = dbActions.userLogin(loginData.userId, loginData.password)
    return userDetails

@router.get("/allMotivations")
def get_all_motivations(locale):
    dbActions = moovDBInstance()
    motivationsDetails = dbActions.getAllMotivations (int(locale))

    return motivationsDetails

@router.get("/userMotivations")
def get_user_motivations(userId, locale):
    dbActions = moovDBInstance()
    motivationsDetails = dbActions.getUserMotivations (userId, int(locale))

    return motivationsDetails


@router.get("/user")
def get_user(id, mail = ""):
    dbActions = moovDBInstance()
    userDetails = dbActions.getUser (id, mail)

    return userDetails

@router.post("/addUser")
def add_or_update_user(id, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", personsOfInterest = []):
    dbActions = moovDBInstance()
    dbActions.insertOrUpdateUserDetails(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=int(locale), gender=gender, orgId = orgId, role=role, mailAddress=mailAddress, motivations={}, personsOfInterest=personsOfInterest)

    return 

@router.post("/setMotivations")
def set_motivations_to_user(id, motivations):
    dbActions = moovDBInstance()
    userDetails = dbActions.setMotivationsToUSer (id, ast.literal_eval(motivations))

    return userDetails

@router.get("/question")
def get_question(id, locale):
    dbActions = moovDBInstance()
    questionDetails = dbActions.getQuestion(id, int(locale))

    return questionDetails
    
@router.get("/startUserJourney")
def start_user_journey(userId):
    journeyId = userDiscoveryJourney.startUserJourney(userId)
    
    return journeyId

@router.get("/journeyGetNextBatch")
def get_next_questions_batch(userId):
    questionsBatch = userDiscoveryJourney.getNextQuestionsBatch(userId)
    
    return questionsBatch

@router.get("/journeySetQuestionResponse", status_code=200)
def set_journey_question_response(userId, questionId, responseId):
    userDiscoveryJourney.setUserResponse (userId = userId, questionId = questionId, responseId = responseId)

    return "reposne was set"

@router.get("/journeySetQuestionMultipleResponse", status_code=200)
def set_journey_multiple_question_responses(userId, questionId, responses):
    userDiscoveryJourney.setUserMultipleResponses (userId = userId, questionId = questionId, responses = responses)

    return "reposnes were set"

@router.get("/getUserCircle", status_code=200)
def get_user_circle(userId):
    dbActions = moovDBInstance()
    userCircleDetails = dbActions.getUserCircle(userId=userId)
    return userCircleDetails

@router.get("/allSubjects")
def get_all_subjects(locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    subjectsDetails = dbActions.getAllSubjects(int(locale))
    
    return subjectsDetails

@router.get("/issuesForSubject")
def get_issue_for_subjects(subjectId, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssuesForSubject(subjectId, int(locale))
    
    return issuesDetails

@router.get("/issue")
def get_issue(id, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    issueDetails = dbActions.getIssue(id, int(locale))
    
    return issueDetails

@router.get("/allIssues")
def get_all_issues(locale):
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getAllIssues(int(locale))
    
    return issuesDetails

@router.get("/issueForUser")
def get_issue_for_user(issueId, userId, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssueForUser(issueId, userId, int(locale))
    
    return issuesDetails

@router.get("/moov")
def get_moov(id, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    moovDetails = dbActions.getMoov(id, int(locale))
    
    return moovDetails

@router.get("/moovsForIssueAndUser")
def get_moovs_for_issue_and_user(issueId, userId, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    moovsDetails = dbActions.getMoovsForIssueAndUser(issueId=issueId, userId=userId, locale=int(locale))
    
    return moovsDetails

@router.get("/activateMoov")
def activate_moov(moovId, userId, counterpartId):
    dbActions = moovDBInstance()
    
    returnValue = dbActions.activateMoov(moovId=moovId, userId=userId, counterpartId=counterpartId)
    
    return returnValue

@router.get("/endMoov")
def end_moov (activeMoovId, feedbackScore, feedbackText):
    dbActions = moovDBInstance()
    
    returnValue = dbActions.endMoov(activeMoovId=activeMoovId, feedbackScore=feedbackScore, feedbackText=feedbackText)
    
    return returnValue

@router.get("/activeMoovsForCounterpart")
def get_active_moovs_to_counterpart (userId, counterpartId, locale=Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    activeMoovs = dbActions.getActiveMoovsToCounterpart(userId=userId, counterpartId=counterpartId, locale=int(locale))
    
    return activeMoovs

@router.get("/activeMoovsForUser")
def get_active_moov_for_user (userId, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    activeMoovs = dbActions.getActiveMoovsForUser(userId=userId, locale=int(locale))
    
    return activeMoovs
