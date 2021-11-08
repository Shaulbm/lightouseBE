from fastapi import Header, APIRouter
from fastapi import HTTPException
from pymongo.common import MIN_SUPPORTED_SERVER_VERSION
from mongoDB import moovDBInstance
import userDiscoveryJourney
from generalData import UserRoles, Gender, Locale
from loguru import logger

router = APIRouter()

@router.get("/motivation")
def get_motivation(id, locale):
    dbActions = moovDBInstance()
    motivationDetails = dbActions.getMotivation (id,int(locale))

    return motivationDetails

@router.get("/allMotivations")
def get_all_motivations(locale):
    dbActions = moovDBInstance()
    motivationsDetails = dbActions.getAllMotivations (int(locale))

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
    userDetails = dbActions.setMotivationsToUSer (id, motivations)

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

@router.get("/issue")
def get_issue(id, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssue(id, int(locale))
    
    return issuesDetails

@router.get("/issueForUser")
def get_issue_for_user(id, userId, locale = Locale.UNKNOWN):
    dbActions = moovDBInstance()
    
    issuesDetails = dbActions.getIssueForUser(id, userId, int(locale))
    
    return issuesDetails