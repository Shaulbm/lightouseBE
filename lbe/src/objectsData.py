from enum import Enum

class UserRoles(Enum):
    UNKNOWN = 1
    USER = 2
    MANAGER = 3
    HR = 4

class UserMinimalData:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class UserData:
    def __init__(self, id = None, name  = None, mail = None, role = None, managerId = None, status = None, currentIssue = None, trainingStage = None, courseLesson = None, userAttributes = None, userDetails = None):
        if (userDetails is None):
            self.id = id
            self.name = name
            self.mail = mail
            self.role = role
            self.managerId = managerId
            self.status = status
            self.currentIssue = currentIssue
            self.trainingStage = trainingStage
            self.courseLesson = courseLesson
            
            if (userAttributes is None):
                self.userAttributes = None
            else:
                self.userAttributes = userAttributes.copy()

        else:
            # parse from json

            # mandatory fields
            self.id = userDetails['id']
            self.name = userDetails['name']
            self.orgId = userDetails['orgId']

            # non mandatory fields - set default values:
            self.mail = ''
            self.role = UserRoles.UNKNOWN
            self.managerId = ''
            self.status = ''
            self.currentIssue = ''
            self.trainingStage = ''
            self.userAttributes = None

            # non mandatory values - set only if existing
            if ('mail' in userDetails):
                self.mail = userDetails['mail']

            if ('role' in userDetails):
                if (userDetails['role'] == 'user'):
                    self.role = UserRoles.USER
                elif (userDetails['role'] == 'manager'):
                    self.role = UserRoles.MANAGER
                elif (userDetails['role'] == 'hr'):
                    self.role = UserRoles.HR

            if ('managerId' in userDetails):
                self.managerId = userDetails['managerId']

            if ('status' in userDetails):
                self.status = userDetails['status']

            if ('currentIssue' in userDetails):    
                self.currentIssue = userDetails['currentIssue']
            
            if ('trainingStage' in userDetails): 
                self.trainingStage = userDetails['trainingStage']

            if ('courseLesson' in userDetails):
                self.courseLesson = userDetails['courseLesson']

            if ('attributes' in userDetails):
                if (len(userDetails['attributes']) > 0):            
                    self.userAttributes = userDetails['attributes'].copy()


class UserAttributesData:
    def __init__(self, userId = None, demographicData = None, userAttributes = None, userAttributesDetails = None):
        if (userAttributesDetails is None):
            self.userId = userId

            if (demographicData is None):
                self.demographicData = None
            else:
                self.demographicData = demographicData.copy()

            if (userAttributes is None):
                self.userAttributes = None
            else:
                self.userAttributes = userAttributes.copy()

        else:
            # parse from json

            # mandatory fields
            self.userId = userAttributesDetails['userId']

            if ('demographicData' in userAttributesDetails):
                if (len(userAttributesDetails['demographicData']) > 0):            
                    self.demographicData = userAttributesDetails['demographicData'].copy()

            if ('attributes' in userAttributesDetails):
                if (len(userAttributesDetails['attributes']) > 0):            
                    self.userAttributes = userAttributesDetails['attributes'].copy()

class organizationData:
    def __init__(self, id = None, name = None, url = None, orgDetails = None):
        if (orgDetails is None):
            self.id = id
            self.name = name
            self.url = url

        else:
            # parse from JSON

            # mandatory fields
            self.id = orgDetails['id']
            self.name = orgDetails['name']

            # non mandatory fields - set default values:
            self.url = ''

            # non mandatory values - set only if existing
            if ('url' in orgDetails):
                self.mail = orgDetails['url']

class trainingStageData:
    def __init__(self, id = None, trainingId  = None, challengeNumber = None, shortDescription = None, timespan = None, descriptionInDetails = None, trainingStageDetails = None):
        if (trainingStageDetails is None):
            self.id = id
            self.trainingId = trainingId
            self.challengeNumber = challengeNumber
            self.shortDescription = shortDescription
            self.descriptionInDetails = descriptionInDetails
            self.timeSpan = timespan

        else:
            # parse from json

            # mandatory fields
            self.id = trainingStageDetails['id']
            self.trainingId = trainingStageDetails['trainingId']
            self.challengeNumber = trainingStageDetails['challengeNumber']

            # non mandatory fields - set default values:
            self.shortDescription = ''
            self.descriptionInDetails = ''
            self.timeSpan = ''

            # non mandatory values - set only if existing
            if ('shortDescription' in trainingStageDetails):
                self.shortDescription = trainingStageDetails['shortDescription']

            if ('descriptionInDetails' in trainingStageDetails):    
                self.descriptionInDetails = trainingStageDetails['descriptionInDetails']

            if ('timespan' in trainingStageDetails):    
                self.timeSpan = trainingStageDetails['timeSpan']            

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
            self.id = trainingDetails['id']
            self.name = trainingDetails['name']
            self.issueId = trainingDetails['issueId']

            # non mandatory fields - set default values:
            self.description = ''
            self.challengesNo = ''

            # non mandatory values - set only if existing
            if ('description' in trainingDetails):
                self.description = trainingDetails['description']

            if ('challengesNumber' in trainingDetails):
                self.challengesNo = trainingDetails['challengesNumber']

class courseLessonData:
    def __init__(self, id = None, courseId  = None, lessonNumber = None, shortDescription = None, timeSpan = None, videoURL = None, courseLessonDetails = None):
        if (courseLessonDetails is None):
            self.id = id
            self.courseId = courseId
            self.lessonNumber = lessonNumber
            self.shortDescription = shortDescription
            self.timeSpan = timeSpan
            self.videoURL = videoURL

        else:
            # parse from json

            # mandatory fields
            self.id = courseLessonDetails['id']
            self.courseId = courseLessonDetails['courseId']
            self.lessonNumber = courseLessonDetails['lessonNumber']

            # non mandatory fields - set default values:
            self.shortDescription = ''
            self.videoURL = ''
            self.timeSpan = ''

            # non mandatory values - set only if existing
            if ('shortDescription' in courseLessonDetails):
                self.shortDescription = courseLessonDetails['shortDescription']

            if ('timeSpan' in courseLessonDetails):
                self.timeSpan = courseLessonDetails['timeSpan']

            if ('videoURL' in courseLessonDetails):    
                self.videoURL = courseLessonDetails['videoURL']


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
            self.id = courseDetails['id']
            self.name = courseDetails['name']
            self.issueId = courseDetails['issueId']

            # non mandatory fields - set default values:
            self.description = ''
            self.partsNumber = ''

            # non mandatory values - set only if existing
            if ('description' in courseDetails):
                self.description = courseDetails['description']

            if ('partsNumber' in courseDetails):
                self.partsNumber = courseDetails['partsNumber']

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
            self.id = courseLessonDetails['id']
            self.courseId = courseLessonDetails['courseId']
            self.lessonNumber = courseLessonDetails['lessonNumber']

            # non mandatory fields - set default values:
            self.shortDescription = ''
            self.videoURL = ''

            # non mandatory values - set only if existing
            if ('shortDescription' in courseLessonDetails):
                self.shortDescription = courseLessonDetails['shortDescription']

            if ('videoURL' in courseLessonDetails):    
                self.videoURL = courseLessonDetails['videoURL']


class additionalInfoData:
    def __init__(self, id = None, issueId = None, infoType = None, name  = None, description = None, url = None, additionalInfoDetails = None):
        if (additionalInfoDetails is None):
            self.id = id
            self.issueId = issueId
            self.infoType = infoType
            self.name = name
            self.description = description
            self.url = url

        else:
            # parse from json

            # mandatory fields
            self.id = additionalInfoDetails['id']
            self.name = additionalInfoDetails['name']
            self.issueId = additionalInfoDetails['issueId']
            self.infoType = additionalInfoDetails['type']

            # non mandatory fields - set default values:
            self.description = ''
            self.url = ''

            # non mandatory values - set only if existing
            if ('description' in additionalInfoDetails):
                self.description = additionalInfoDetails['description']

            if ('url' in additionalInfoDetails):
                self.url = additionalInfoDetails['url']

class issueData:
    def __init__(self,  id = None, name  = None, description = None, issuseDetails = None):
        if (issuseDetails is None):
            self.id = id
            self.name = name
            self.description = description

        else:
            #parse from json

            #mandatory fields
            self.id = issuseDetails['id']
            self.name = issuseDetails['name']
            self.description = issuseDetails['description']

class trainingMapData:
    def __init__(self, stageData):
        self.currentStage = stageData
        self.pastStages = []
        self.futureStages = []
        pass

class attributesDeltaData:
    def __init__(self) -> None:
        pass

class questionOptionData: 
    def __init__ (self, idx = None, text = None, attributesDelta = None, questionOptionDetails = None):
        if (questionOptionDetails is None):
            self.idx = idx
            self.text = text
            self.attributeDetla = None

            if (attributesDelta is not None):
                self.attributeDetla = attributesDelta.copy()

        else:
            #parse from list 
            # mandatory fields
            self.idx = questionOptionDetails['idx']
            self.text = questionOptionDetails['text']
            self.attributeDetla = questionOptionDetails['attributes'].copy()

class questionRangeData: 
    def __init__ (self, minText = None, maxText = None, rangeValue = None, minAttributesDelta = None, maxAttributesDelta = None, questionRangeDetails = None):
        if (questionRangeDetails is None):
            self.minText = minText
            self.maxText = maxText
            self.rangeValue = rangeValue
            self.minAttributesDelta = None
            self.maxAttributesDelta = None
                
            if (minAttributesDelta is not None):
                self.minAttributesDelta = minAttributesDelta.copy()

            if (maxAttributesDelta is not None):
                self.maxAttributesDelta = maxAttributesDelta.copy()

        else:
            #parse from list 
            # mandatory fields
            self.minText = questionRangeDetails['min']['text']
            self.maxText = questionRangeDetails['max']['text']
            self.rangeValue = questionRangeDetails['rangeValue']
            self.minAttributesDelta = None
            self.maxAttributesDelta = None

            if ('attributes' in questionRangeDetails['min']):
                if (len(questionRangeDetails['min']['attributes']) > 0):
                    self.minAttributesDelta = questionRangeDetails['min']['attributes'].copy()
            
            if ('attributes' in questionRangeDetails['max']):
                if (len(questionRangeDetails['max']['attributes']) > 0):            
                    self.maxAttributesDelta = questionRangeDetails['max']['attributes'].copy()

class questionBoolOptionsData: 
    def __init__ (self, attributesDeltaForYes = None, attributesDeltaForNo = None, questionBoolOptionsDetails = None):
        if (questionBoolOptionsDetails is None):
            if (attributesDeltaForYes is not None):
                self.attributesDeltaForYes = attributesDeltaForYes.copy()

            if (attributesDeltaForNo is not None):
                self.attributesDeltaForNo = attributesDeltaForNo.copy()

        else:
            #parse from list 
            # mandatory fields
            self.attributesDeltaForYes = None
            self.attributesDeltaForNo = None

            if ('attributes' in questionBoolOptionsDetails['Yes']):
                if (len(questionBoolOptionsDetails['Yes']['attributes']) > 0):
                    self.attributesDeltaForYes = questionBoolOptionsDetails['Yes']['attributes'].copy()
            
            if ('attributes' in questionBoolOptionsDetails['No']):
                if (len(questionBoolOptionsDetails['No']['attributes']) > 0):            
                    self.attributesDeltaForNo = questionBoolOptionsDetails['No']['attributes'].copy()

class questionData:
    def __init__(self, id = None, text = None, stage = None, questionType = None, options = None, range = None, boolOptions = None, questionDetails = None):
        if (questionDetails is None):
            self.id = id
            self.text = text
            self.stage = stage
            self.Questiontype = questionType
            self.options = None
            self.range = None
            self.boolOptions = None

            if (options is not None):
                self.options = options.copy()

            if (range is not None):
                self.range = range.copy()

            if (boolOptions is not None):
                self.boolOptions = boolOptions.copy()

        else:
            #parse from list
            # mandatory fields
            self.id = questionDetails['id']
            self.text = questionDetails['text']
            self.stage = questionDetails['stage']
            self.Questiontype = questionDetails['type']
            self.options = None
            self.range = None
            self.boolOptions = None

            if ('options' in questionDetails):
                optionsDBG = questionDetails['options']
                if (len(questionDetails['options']) > 0):
                    self.options = []

                    #create options list
                    for currOptionIdx in questionDetails['options']:
                        self.options.append(questionOptionData(questionOptionDetails = questionDetails['options'][currOptionIdx]))

            if ('range' in questionDetails):
                if (len (questionDetails['range']) > 0):
                    self.range = questionRangeData(questionRangeDetails = questionDetails['range'])

            if ('boolOptions' in questionDetails):
                if (len (questionDetails['boolOptions']) > 0):
                    self.boolOptions = questionBoolOptionsData(questionBoolOptionsDetails = questionDetails['boolOptions'])