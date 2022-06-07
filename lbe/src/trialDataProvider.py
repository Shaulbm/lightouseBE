import datetime
import math
import random
import uuid
from generalData import UserMotivationData
from generalData import AccountType, DiscoveryStatus, Locale, UserData, UserRoles
from environmentProvider import EnvKeys
from generalData import Gender, TrialData
import environmentProvider as ep
from moovLogic import MoovLogic


def createTrialUser (orgName, userFirstName, userLastName, userMailAddress, userGender, locale=Locale.LOCALE_EN_US, useDefaulsPassword=False):
    dbInstance = MoovLogic()
    orgId = orgName + "_" + str(uuid.uuid4())
    startDate=datetime.datetime.utcnow()
    endDate = startDate + datetime.timedelta(days=ep.getAttribute(EnvKeys.trial, EnvKeys.trialPeriodDays))
    trial = TrialData(id= str(uuid.uuid4()), userMail=userMailAddress, orgName=orgId, startDate=startDate, plannedEndDate=endDate)

    dbInstance.insertOrUpdateTrial(trialDetails=trial)

    # Trial User
    userMotivations = {}
    userMotivations['M023'] = UserMotivationData(motivationId='M023', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M006'] = UserMotivationData(motivationId='M006', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M017'] = UserMotivationData(motivationId='M017', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M002'] = UserMotivationData(motivationId='M002', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M027'] = UserMotivationData(motivationId='M027', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    
    newUSerId = dbInstance.createUser(notifyNewUser=False, firstName=userFirstName, familyName=userLastName, accountType=AccountType.TRIAL, gender=userGender, locale=locale, orgId=orgId, role=UserRoles.MANAGER, mailAddress=userMailAddress, motivations=userMotivations, setDefaultPassword=useDefaulsPassword)
    dbInstance.setUserDiscoveryStatus(newUSerId, discoveryStatus= DiscoveryStatus.DISCOVERED)

    createUsersUnder(newUSerId=newUSerId, orgId=orgId, locale=locale)

    return newUSerId

def createUsersUnder(newUSerId, orgId, locale = Locale.LOCALE_EN_US):
    dbInstance = MoovLogic()

    #Sub 1
    userMotivations = {}
    userMotivations['M005'] = UserMotivationData(motivationId='M005', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M020'] = UserMotivationData(motivationId='M020', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M019'] = UserMotivationData(motivationId='M019', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M026'] = UserMotivationData(motivationId='M026', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M002'] = UserMotivationData(motivationId='M002', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    
    userMailAddress = 'sveta@trialemployee.'+orgId+'.com'
    firstName = ('sveta' if locale == Locale.LOCALE_EN_US else 'סבטה')
    lastName = ('shifrin' if locale == Locale.LOCALE_EN_US else 'שיפרין')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.FEMALE, locale=locale,orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations, accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=4, chanceOfSeperation=5)

    #Sub 2
    userMotivations = {}
    userMotivations['M007'] = UserMotivationData(motivationId='M007', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M008'] = UserMotivationData(motivationId='M008', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M028'] = UserMotivationData(motivationId='M028', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M023'] = UserMotivationData(motivationId='M023', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M013'] = UserMotivationData(motivationId='M013', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    
    userMailAddress = 'guy@trialemployee.'+orgId+'.com'
    firstName = ('guy' if locale == Locale.LOCALE_EN_US else 'גיא')
    lastName = ('cohen' if locale == Locale.LOCALE_EN_US else 'כהן')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.MALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=5, chanceOfSeperation=3)

    #Sub 3
    userMotivations = {}
    userMotivations['M002'] = UserMotivationData(motivationId='M002', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M003'] = UserMotivationData(motivationId='M003', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M004'] = UserMotivationData(motivationId='M004', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M014'] = UserMotivationData(motivationId='M014', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M027'] = UserMotivationData(motivationId='M027', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    
    userMailAddress = 'shani@trialemployee.'+orgId+'.com'
    firstName = ('shani' if locale == Locale.LOCALE_EN_US else 'שני')
    lastName = ('birenbaum' if locale == Locale.LOCALE_EN_US else 'בירנבוים')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.FEMALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=3, chanceOfSeperation=4)

    #Sub 4
    userMotivations = {}
    userMotivations['M028'] = UserMotivationData(motivationId='M028', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M008'] = UserMotivationData(motivationId='M008', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M018'] = UserMotivationData(motivationId='M018', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M029'] = UserMotivationData(motivationId='M029', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M021'] = UserMotivationData(motivationId='M021', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    
    userMailAddress = 'revital@trialemployee.'+orgId+'.com'
    firstName = ('revital' if locale == Locale.LOCALE_EN_US else 'רויטל')
    lastName = ('michaelson' if locale == Locale.LOCALE_EN_US else 'מיכלזון')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.FEMALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=5, chanceOfSeperation=2)

    #Sub 5
    userMotivations = {}
    userMotivations['M022'] = UserMotivationData(motivationId='M022', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M021'] = UserMotivationData(motivationId='M021', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M002'] = UserMotivationData(motivationId='M002', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M018'] = UserMotivationData(motivationId='M018', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M019'] = UserMotivationData(motivationId='M019', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    
    userMailAddress = 'moshe@trialemployee.'+orgId+'.com'
    firstName = ('moshe' if locale == Locale.LOCALE_EN_US else 'משה')
    lastName = ('gilboa' if locale == Locale.LOCALE_EN_US else 'גלבוע')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.MALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=5, chanceOfSeperation=3)

    #Sub 6
    userMotivations = {}
    userMotivations['M020'] = UserMotivationData(motivationId='M020', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M017'] = UserMotivationData(motivationId='M017', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=2)
    userMotivations['M025'] = UserMotivationData(motivationId='M025', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M024'] = UserMotivationData(motivationId='M024', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=1)
    userMotivations['M006'] = UserMotivationData(motivationId='M006', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    
    userMailAddress = 'aharon@trialemployee.'+orgId+'.com'
    firstName = ('aharon' if locale == Locale.LOCALE_EN_US else 'אהרן')
    lastName = ('shahar' if locale == Locale.LOCALE_EN_US else 'שחר')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.MALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=4, chanceOfSeperation=4)

    #Sub 7
    userMotivations = {}
    userMotivations['M010'] = UserMotivationData(motivationId='M010', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M012'] = UserMotivationData(motivationId='M012', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=3)
    userMotivations['M029'] = UserMotivationData(motivationId='M029', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=2)
    userMotivations['M006'] = UserMotivationData(motivationId='M006', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M016'] = UserMotivationData(motivationId='M016', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    
    userMailAddress = 'mike@trialemployee.'+orgId+'.com'
    firstName = ('mike' if locale == Locale.LOCALE_EN_US else 'מייק')
    lastName = ('levinson' if locale == Locale.LOCALE_EN_US else 'לוינסון')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.MALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=3, chanceOfSeperation=3)

    #Sub 8 - haveb't finish discovery
    userMotivations = {}
    userMotivations['M015'] = UserMotivationData(motivationId='M015', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M014'] = UserMotivationData(motivationId='M014', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M026'] = UserMotivationData(motivationId='M026', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=4)
    userMotivations['M003'] = UserMotivationData(motivationId='M003', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    userMotivations['M002'] = UserMotivationData(motivationId='M002', journeyScore=((math.floor ((random.uniform (a=2.6, b=5.2))*10))/10.0), gapFactor=5)
    
    userMailAddress = 'michal@trialemployee.'+orgId+'.com'
    firstName = ('michal' if locale == Locale.LOCALE_EN_US else 'מיכל')
    lastName = ('levi' if locale == Locale.LOCALE_EN_US else 'לוי')
    subUser = dbInstance.createUser( parentId=newUSerId, firstName=firstName, familyName=lastName, mailAddress=userMailAddress, gender=Gender.FEMALE, locale=locale, orgId=orgId, role=UserRoles.EMPLOYEE, motivations=userMotivations,  accountType=AccountType.TRIAL)
    dbInstance.setUserDiscoveryStatus(subUser, discoveryStatus= DiscoveryStatus.DISCOVERED)
    dbInstance.insertOrUpdateRelationshipDetails(userId=newUSerId, counterpartId=subUser, costOfSeperation=5, chanceOfSeperation=4)

def deleteTrialData(trialId):
    dbInstance = MoovLogic()

    trialDetails = dbInstance.getTrialDetails(trialId=trialId)

    if trialDetails is None:
        return

    userDetails = dbInstance.getUserByMail(trialDetails.userMail)

    # delete all moovs, relationship, history, users under, credentials.