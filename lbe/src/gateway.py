from fastapi import Header, APIRouter, Request, Response
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pymongo.common import MIN_SUPPORTED_SERVER_VERSION
from moovLogic import MoovLogic
import userDiscoveryJourney
from generalData import UserRoles, Gender, Locale, UserContextData
from loguru import logger
import ast
from pydantic import BaseModel

router = APIRouter()

class LoginData(BaseModel):
    userMail: str
    password: str

class EndMoovData(BaseModel):
    activeMoovId: str
    feedbackScore: int
    feedbackText: str

class UpdateUserData(BaseModel):
    userId: str
    locale: str
    gender: int

class RelationshipData (BaseModel):
    userId: str
    counterpartId: str
    costOfSeperation: int
    chanceOfSeperation: int

class UserFeedbackData(BaseModel):
    userId: str
    issue: str
    text: str

class UpdatePasswordData(BaseModel):
    userId: str
    oldPassword: str
    newPassword: str

def set_user_context(userId):
    dbActions = MoovLogic()
    return dbActions.setUserContextData(userId)

def get_user_context(request: Request):
    userContextDetails = None
    if ("X-USER-ID" in  request.headers):
        dbActions = MoovLogic()
        userContextDetails = dbActions.getUserContextData(request.headers["X-USER-ID"])

    return userContextDetails

@router.get("/motivation")
def get_motivation(request: Request, id):
    userContextDetails = get_user_context(request)

    dbActions = MoovLogic()
    motivationDetails = dbActions.getMotivation (id, userContextDetails)

    return motivationDetails

@router.post("/login")
def user_log_in(loginData : LoginData):
    dbActions = MoovLogic()
    userDetails = dbActions.userLogin(loginData.userMail, loginData.password)
    return userDetails

@router.get("/allMotivations")
def get_all_motivations(request: Request):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    motivationsDetails = dbActions.getAllMotivations (userContextDetails)

    return motivationsDetails

@router.get("/userMotivations")
def get_user_motivations(request: Request, userId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    motivationsDetails = dbActions.getUserMotivations (userId, userContextDetails)

    return motivationsDetails


@router.get("/user")
def get_user(request: Request, id):
    dbActions = MoovLogic()

    userDetails = dbActions.getUser (id)

    return userDetails

@router.post("/addUser")
def add_or_update_user(request: Request, id, parentId = "", firstName = "", familyName = "", gender = Gender.MALE, locale = Locale.UNKNOWN, orgId = "", role = UserRoles.NONE, mailAddress = "", personsOfInterest = []):
    dbActions = MoovLogic()
    dbActions.insertOrUpdateUserDetails(id=id, parentId=parentId, firstName=firstName, familyName= familyName, locale=int(locale), gender=gender, orgId = orgId, role=role, mailAddress=mailAddress, motivations={}, personsOfInterest=personsOfInterest)

    return 

@router.post("/setMotivations")
def set_motivations_to_user(request: Request, id, motivations):
    dbActions = MoovLogic()
    # print ("in set_motivaitons_to_user, motivations are {0}", str(motivations) )
    userDetails = dbActions.setMotivationsToUSer (id, ast.literal_eval(motivations))

    return userDetails

@router.get("/question")
def get_question(request: Request, id):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    questionDetails = dbActions.getQuestion(id, userContextDetails)

    return questionDetails
    
@router.get("/startUserJourney")
def start_user_journey(request: Request, userId):
    journeyId = userDiscoveryJourney.startUserJourney(userId)
    
    return journeyId

@router.get("/continueUserJourney")
def continue_user_journey(request: Request, userId):
    journeyId = userDiscoveryJourney.continueUserJourney(userId)
    
    return journeyId


@router.get("/journeyGetQuestionsInBatch")
def get_next_questions_batch(request: Request, userId):
    userContextDetails = get_user_context(request)
    questionsBatch = userDiscoveryJourney.getQuestionsInBatch(userId, userContext=userContextDetails)
    
    return questionsBatch

@router.get("/journeyGetCurrentBatch")
def get_current_questions_batch(request: Request, userId):
    userContextDetails = get_user_context(request)
    questionsBatch = userDiscoveryJourney.getCurrentQuestionsBatch(userId, userContext=userContextDetails)
    
    return questionsBatch

@router.get("/journeySetQuestionResponse", status_code=200)
def set_journey_question_response(request: Request, userId, questionId, responseId):
    userContextDetails = get_user_context(request)
    userDiscoveryJourney.setUserResponse (userId = userId, questionId = questionId, responseId = responseId, userContext=userContextDetails)

    return "reposne was set"

@router.get("/journeySetQuestionMultipleResponse", status_code=200)
def set_journey_multiple_question_responses(request: Request, userId, questionId, responses):
    userDiscoveryJourney.setUserMultipleResponses (userId = userId, questionId = questionId, responsesIds = responses)

    return "reposnes were set"

@router.get("/getUserCircle", status_code=200)
def get_user_circle(request: Request, userId):
    print ('in get_user_circle, UserID is {0}', userId)

    dbActions = MoovLogic()
    userCircleDetails = dbActions.getUserCircle(userId=userId)
    return userCircleDetails

@router.get("/allSubjects")
def get_all_subjects(request: Request, locale = Locale.UNKNOWN):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    subjectsDetails = dbActions.getAllSubjects(userContextDetails)
    
    return subjectsDetails

@router.get("/issuesForSubject")
def get_issue_for_subjects(request : Request, subjectId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    issuesDetails = dbActions.getIssuesForSubject(subjectId, userContextDetails)
    
    return issuesDetails

@router.get("/issue")
def get_issue(request: Request, id):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    issueDetails = dbActions.getIssue(id, userContextDetails)
    
    return issueDetails

@router.get("/allIssues")
def get_all_issues(request: Request, counterpartId = ""):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    issuesDetails = dbActions.getAllIssues(counterpartId, userContextDetails)
    
    return issuesDetails

@router.get("/issueForUser")
def get_issue_for_user(request: Request, issueId, userId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    issuesDetails = dbActions.getIssueForCounterpart(issueId, userId, userContextDetails)
    
    return issuesDetails

# @router.get("/moov")
# def get_moov(request: Request, id):
#     userContextDetails = get_user_context(request)
#     dbActions = MoovLogic()
    
#     moovDetails = dbActions.getIssueMoov(id, userContextDetails)
    
#     return moovDetails

@router.get("/moovsForIssueAndUser")
def get_moovs_for_issue_and_user(request: Request, issueId, userId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    moovsDetails = dbActions.getMoovsForIssueAndCounterpart(issueId=issueId, counterpartId=userId, userContext= userContextDetails)
    
    return moovsDetails

@router.get("/activateMoov")
def activate_moov(request: Request, moovId, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    returnValue = dbActions.activateIssueMoov(moovId=moovId, userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return returnValue

@router.get("/activateConflictMoov")
def activate_conflict_moov(request: Request, moovId, userId, firstCounterpartId, secondCounterpartId):
    counterpartsIds = [firstCounterpartId, secondCounterpartId]
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    returnValue = dbActions.activateConflictMoov(moovId=moovId, userId=userId, counterpartsIds=counterpartsIds, userContext=userContextDetails)
    
    return returnValue

@router.post("/endMoov")
def end_moov (request: Request, endMoovDetails: EndMoovData):
    dbActions = MoovLogic()
    
    returnValue = dbActions.endMoov(activeMoovId=endMoovDetails.activeMoovId, feedbackScore=endMoovDetails.feedbackScore, feedbackText=endMoovDetails.feedbackText, isEndedByTimer=False)
    
    return returnValue

@router.get("/activeMoovsForCounterpart")
def get_active_moovs_to_counterpart (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    activeMoovs = dbActions.getActiveMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return activeMoovs

@router.get("/pastMoovsForCounterpart")
def get_past_moovs_to_counterpart (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    activeMoovs = dbActions.getPastMoovsToCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return activeMoovs

@router.get("/pastMoovsForMoovAndCounterpart")
def get_past_moovs_to_moov_and_counterpart (request: Request, userId, counterpartId, moovId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    activeMoovs = dbActions.getPastMoovsToMoovAndCounterpart(userId=userId, counterpartId=counterpartId, moovId=moovId, userContext=userContextDetails)
    
    return activeMoovs


@router.get("/activeMoovsForUser")
def get_active_moovs_for_user (request: Request, userId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    activeMoovs = dbActions.getActiveMoovsForUser(userId=userId, userContext=userContextDetails)
    
    return activeMoovs

@router.get("/userImage", response_class=FileResponse)
def get_user_image (request: Request, userId):
    dbActions = MoovLogic()
    
    userImagePath = dbActions.getUserImageFromFile(userId=userId)
    
    return userImagePath

@router.get("/conflictsForUsers")
def get_conflicts_for_users (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    usersConflicts = dbActions.getConflictsForUsers(teamMemberId=userId,counterpartId=counterpartId, partialData=False ,userContext=userContextDetails)
    
    return usersConflicts

@router.get("/conflictsMoovsForUsers")
def get_all_conflicts_moovs_for_users (request: Request, teamMemberId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    conflictMoovs = dbActions.getConflictsMoovsForUsers(teamMemberId=teamMemberId,counterpartId=counterpartId, userContext=userContextDetails)
    
    return conflictMoovs

@router.get("/conflictMoovs")
def get_conflict_moovs (request: Request, conflictId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    conflictMoovs = dbActions.getConflictMoovs(conflictId=conflictId, userContext=userContextDetails)
    
    return conflictMoovs

@router.post("/updateRelationship")
def update_relationship_data(request: Request, relationshipDetails: RelationshipData):
    dbActions = MoovLogic()
    
    dbActions.insertOrUpdateRelationshipDetails(userId=relationshipDetails.userId, counterpartId=relationshipDetails.counterpartId, costOfSeperation=relationshipDetails.costOfSeperation, chanceOfSeperation=relationshipDetails.chanceOfSeperation)
    
    return Response(status_code=201)

@router.get("/getTopRecommendedMoovs")
def get_top_recommended_moovs (request: Request, userId, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()
    
    topRecommendedMoovs = dbActions.getTopRecommendedMoovsForCounterpart(userId=userId, counterpartId=counterpartId, userContext=userContextDetails)
    
    return topRecommendedMoovs

@router.get("/isMissingRelationshipData")
def is_missing_relationship_data(request: Request, userId, counterpartId):
    dbActions = MoovLogic()
    
    returnValue = dbActions.missingRelationshipData(userId=userId, counterpartId=counterpartId)
    
    return returnValue

@router.get("/extendActiveMoov")
def extend_activeM_moov(request:Request, activeMoovId):
    dbActions = MoovLogic()

    returnValue = dbActions.extendAcctiveMoov(activeMoovId=activeMoovId)

    return returnValue

@router.get("/insightsForCounterpart")
def inights_for_counterpart(request:Request, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()

    returnValue = dbActions.getInsightsForCounterpart(counterpartId=counterpartId, userContext=userContextDetails)

    return returnValue   

@router.get("/insightsForSelf")
def inights_for_self(request:Request):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()

    returnValue = dbActions.getInsightsForSelf(userContext=userContextDetails)

    return returnValue

@router.post("/updateUserDetails")
def update_user_details(request:Request, userDetails: UpdateUserData):
    dbActions = MoovLogic()

    returnValue = dbActions.updateUserDetails(userDetails.userId, userDetails.locale, userDetails.gender)

    return returnValue

@router.post("/updateUserPassword")
def update_user_details(request:Request, passwordDetails: UpdatePasswordData):
    dbActions = MoovLogic()

    returnValue = dbActions.updateUserPassword(passwordDetails.userId, passwordDetails.oldPassword, passwordDetails.newPassword)

    return returnValue

@router.post("/sendFeedback")
def send_feedback(request:Request, feedbackDetails: UserFeedbackData):
    dbActions = MoovLogic()

    returnValue = dbActions.sendUserFeedback(userId = feedbackDetails.userId, issue=feedbackDetails.issue, text=feedbackDetails.text)

    return returnValue

@router.post("/sendDiscoveryReminder")
def send_discoveryReminder(request:Request, counterpartId):
    userContextDetails = get_user_context(request)
    dbActions = MoovLogic()

    returnValue = dbActions.sendDiscoveryReminder(counterpartId = counterpartId, userContext=userContextDetails)

    return returnValue

