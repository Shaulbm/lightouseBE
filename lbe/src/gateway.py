from fastapi import Header, APIRouter
from fastapi import HTTPException
from pymongo.common import MIN_SUPPORTED_SERVER_VERSION
from mongoDB import moovDBInstance
import userDiscoveryJourney
from generalData import UserRoles

router = APIRouter()

@router.get("/motivation")
def get_motivation(id, locale):
    dbActions = moovDBInstance()
    motivationDetails = dbActions.getMotivation (id,int(locale))

    return motivationDetails

@router.get("/user")
def get_user(id, mail = ""):
    dbActions = moovDBInstance()
    userDetails = dbActions.getUser (id, mail)

    return userDetails

@router.post("/addUser")
def add_or_update_user(id, mail = "", parentId = "", firstName = "", familyName = "", role = UserRoles.NONE, mailAddress = "", motivations = {}, personsOfInterest = []):
    dbActions = moovDBInstance()
    dbActions.insertOrUpdateUserDetails(id=id, parentId=parentId, firstName=firstName, familyName= familyName, role=role, mailAddress=mail, motivations=motivations, personsOfInterest=personsOfInterest)

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
def get_next_questions_batch(userId, locale):
    questionsBatch = userDiscoveryJourney.getNextQuestionsBatch(userId, locale)
    
    return questionsBatch

@router.get("/journeySetQuestionResponse", status_code=200)
def set_journey_question_response(userId, questionId, responseId):
    userDiscoveryJourney.setUserResponse (userId = userId, questionId = questionId, responseId = responseId)

    return "reposne was set"

@router.get("/journeySetQuestionMultipleResponse", status_code=200)
def set_journey_multiple_question_responses(userId, questionId, responses):
    userDiscoveryJourney.setUserMultipleResponses (userId = userId, questionId = questionId, responses = responses)

    return "reposnes were set"