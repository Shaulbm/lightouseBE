import users

def startDiscvoery (userName, externalUserName):
    if (userName is None):
        return

    if (externalUserName is not None and externalUserName != userName):
        # this is a request from the user's manager / HR - start external discovery process
        # start a discvoery process for the userName and requestingUserName (there can be several on going processes) 
        pass
    else:
        # the discovery is for the user himself - start self discovery proccess
        '''
        If the user is new - create a userDiscoveryJourney and userProfile data in the DB
        Evaluate user - to get next questions in the DB (nextQuestionPerUser - in the discovery journey entry)

        If the user is not new (the user was reviewed by his manager / HR) - but have not started self discovery yet
        Evaluate User (by the externalDiscoveryDataand the user's Profile data)  - to get next questions in the DB (nextQuestionPerUser - in the discovery journey entry)
        '''
        pass

def getNextSelfDiscoveryQuestions (userName):
    '''
    consider "startDiscovery"
    if there are no more  questions left un answered in the stage in the DB - 
    call selfEvaluate - this will set the evaluationStage, and provide more questions. It can also state - done for now...
    
    return the next question (if there is one after selfEvaluate)
    Also returns whether the process is done enough (as the user might be able to continue after we know enough 
    for purpose of fine tuning).
    ?Save state (what question were answered, what not - to know what is the next question for the UX).
    ?Return the first batch of questions (Stage 1-10 is external review, 10+ self discovery)
    '''
    # reutrn the next questions that needs to get answered
    pass

def getNextExternalDiscoveryQuestions (userName, externalUserName):
    '''if there are no more  questions left un answered in the stage in the DB - 
    increase the stage for the user and calculate the next set of questions 
    Also returns whether the process is done enough (as the user might be able to continue after we know enough 
    for purpose of fine tuning).'''
    # reutrn the next questions that needs to get answered
    pass

def setSelfResponse (userName, questionId, response):
    # save the reponse for the user, update the relevant attributes
    pass

def setExternalResponse (userName, externalUserName, questionId, reponse):
    # save the reponse for the user, update the relevant attributes
    pass

def selfEvaluate (userNane):
    '''
    General - Here we estimate whether the process should continue, and if so - what is the direction of the next couple of questions. 
    As long as we are under MINIMAL_DISCOVERY_STAGE: 
    increase the stage for the user and calculate the next set of questions 

        calculate the relevant Archetypes with their coupling level (stirngly/weakly coupled).
        calculate relevant questions
        select questions by score.

    
    If we are above the MINIMAL_DISCOVERY_STAGE: 
    1. See if the process is can be concluded for now (not have to be all the way done) - 
    2. (Not dependent on #1) Find the possible issues and provide score (who fits best)
    
    Save Results:
    Save next questions
    Save archtypes
    Save possible Issues
    '''
    pass

def externalEvaluate (userNane):
    '''calculate the relevant Archetypes with their coupling level (stirngly/weakly coupled). 
    If the process is somewhat done (not have to be all the way done) - 
    also find the possible issues and provide score (who fits best)'''
    pass
