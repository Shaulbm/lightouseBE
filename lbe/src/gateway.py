from fastapi import Header, APIRouter, Request
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pymongo.common import MIN_SUPPORTED_SERVER_VERSION
from mongoDB import moovDBInstance
import userDiscoveryJourney
from generalData import UserRoles, Gender, Locale, UserContextData
from loguru import logger
import ast
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    userMail: str
    password: str

def set_user_context(userId):
    dbActions = moovDBInstance()
    return dbActions.setUserContextData(userId)

def get_user_context(request: Request):
    userContextDetails = None
    if ("X-USER-ID" in  request.headers):
        dbActions = moovDBInstance()
        userContextDetails = dbActions.getUserContextData(request.headers["X-USER-ID"])

    return userContextDetails

@router.get("/motivation")
def get_motivation(request: Request, id, locale):
    userContextDetails = get_user_context(request)

    dbActions = moovDBInstance()
    motivationDetails = dbActions.getMotivation (id, userContextDetails)

    return motivationDetails

@router.post("/login")
def user_log_in(loginData : LoginData):
    dbActions = moovDBInstance()
    userDetails = dbActions.userLogin(loginData.userMail, loginData.password)
    return userDetails

@router.get("/allMotivations")
def get_all_motivations(request: Request):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    motivationsDetails = dbActions.getAllMotivations (userContextDetails)

    return motivationsDetails

@router.get("/userMotivations")
def get_user_motivations(request: Request, userId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    motivationsDetails = dbActions.getUserMotivations (userId, userContextDetails)

    return motivationsDetails


@router.get("/user")
def get_user(request: Request, id, mail = ""):
    dbActions = moovDBInstance()
    userDetails = dbActions.getUser (id, mail)

    return userDetails

@router.post("/addUser")
def add_or_update_user(request: Request, id, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", personsOfInterest = []):
    dbActions = moovDBInstance()
    dbActions.insertOrUpdateUserDetails(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=int(locale), gender=gender, orgId = orgId, role=role, mailAddress=mailAddress, motivations={}, personsOfInterest=personsOfInterest)

    return 

@router.post("/setMotivations")
def set_motivations_to_user(request: Request, id, motivations):
    dbActions = moovDBInstance()
    userDetails = dbActions.setMotivationsToUSer (id, ast.literal_eval(motivations))

    return userDetails

@router.get("/question")
def get_question(request: Request, id):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    questionDetails = dbActions.getQuestion(id, userContextDetails)

    return questionDetails
    
@router.get("/startUserJourney")
def start_user_journey(request: Request, userId):
    journeyId = userDiscoveryJourney.startUserJourney(userId)
    
    return journeyId

@router.get("/journeyGetNextBatch")
def get_next_questions_batch(request: Request, userId):
    userContextDetails = get_user_context(request)
    questionsBatch = userDiscoveryJourney.getNextQuestionsBatch(userId, userContext=userContextDetails)
    
    return questionsBatch

@router.get("/journeySetQuestionResponse", status_code=200)
def set_journey_question_response(request: Request, userId, questionId, responseId):
    userContextDetails = get_user_context(request)
    userDiscoveryJourney.setUserResponse (userId = userId, questionId = questionId, responseId = responseId, userContext=userContextDetails)

    return "reposne was set"

@router.get("/journeySetQuestionMultipleResponse", status_code=200)
def set_journey_multiple_question_responses(request: Request, userId, questionId, responses):
    userDiscoveryJourney.setUserMultipleResponses (userId = userId, questionId = questionId, responses = responses)

    return "reposnes were set"

@router.get("/getUserCircle", status_code=200)
def get_user_circle(request: Request, userId):
    print ('in get_user_circle, UserID is {0}', userId)

    dbActions = moovDBInstance()
    userCircleDetails = dbActions.getUserCircle(userId=userId)
    return userCircleDetails

@router.get("/allSubjects")
def get_all_subjects(request: Request, locale = Locale.UNKNOWN):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    subjectsDetails = dbActions.getAllSubjects(userContextDetails)
    
    return subjectsDetails

@router.get("/issuesForSubject")
def get_issue_for_subjects(request : Request, subjectId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssuesForSubject(subjectId, userContextDetails)
    
    return issuesDetails

@router.get("/issue")
def get_issue(request: Request, id):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    issueDetails = dbActions.getIssue(id, userContextDetails)
    
    return issueDetails

@router.get("/allIssues")
def get_all_issues(request: Request):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getAllIssues(userContextDetails)
    
    return issuesDetails

@router.get("/issueForUser")
def get_issue_for_user(request: Request, issueId, userId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssueForUser(issueId, userId, userContextDetails)
    
    return issuesDetails

# @router.get("/moov")
# def get_moov(request: Request, id):
#     userContextDetails = get_user_context(request)
#     dbActions = moovDBInstance()
    
#     moovDetails = dbActions.getIssueMoov(id, userContextDetails)
    
#     return moovDetails

@router.get("/moovsForIssueAndUser")
def get_moovs_for_issue_and_user(request: Request, issueId, userId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    moovsDetails = dbActions.getMoovsForIssueAndUser(issueId=issueId, userId=userId, userContext= userContextDetails)
    
    return moovsDetails

@router.get("/activateMoov")
def activate_moov(request: Request, moovId, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    returnValue = dbActions.activateIssueMoov(moovId=moovId, userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return returnValue

@router.get("/activateConflictMoov")
def activate_conflict_moov(request: Request, moovId, userId, firstCounterpartId, secondCounterpartId):
    counterpartsIds = [firstCounterpartId, secondCounterpartId]
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    returnValue = dbActions.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, userContext=userContextDetails)
    
    return returnValue

@router.get("/endMoov")
def end_moov (request: Request, activeMoovId, feedbackScore, feedbackText):
    dbActions = moovDBInstance()
    
    returnValue = dbActions.endMoov(activeMoovId=activeMoovId, feedbackScore=feedbackScore, feedbackText=feedbackText)
    
    return returnValue

@router.get("/activeMoovsForCounterpart")
def get_active_moovs_to_counterpart (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    activeMoovs = dbActions.getActiveMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return activeMoovs

@router.get("/pastMoovsForCounterpart")
def get_past_moovs_to_counterpart (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    activeMoovs = dbActions.getPastMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return activeMoovs


@router.get("/activeMoovsForUser")
def get_active_moov_for_user (request: Request, userId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    activeMoovs = dbActions.getActiveMoovsForUser(userId=userId, userContext=userContextDetails)
    
    return activeMoovs

@router.get("/userImage", response_class=FileResponse)
def get_user_image (request: Request, userId):
    dbActions = moovDBInstance()
    
    userImagePath = dbActions.getUserImageFromFile(userId=userId)
    
    return userImagePath

@router.get("/conflictsForUsers")
def get_conflicts_for_users (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    usersConflicts = dbActions.getConflictsForUsers(userId=userId,counterpartId=counterpartId, userContext=userContextDetails)
    
    return usersConflicts

@router.get("/conflictMoovs")
def get_conflict_moovs (request: Request, conflictId):
    userContextDetails = get_user_context(request)
    dbActions = moovDBInstance()
    
    conflictMoovs = dbActions.getConflictMoovs(conflictId=conflictId, userContext=userContextDetails)
    
    return conflictMoovs
