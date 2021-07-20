class UserData:
    def __init__(self, id = None, name  = None, mail = None, status = None, currentIssue = None, trainingStage = None, courseLesson = None, userDetails = None):
        if (userDetails is None):
            self.id = id
            self.name = name
            self.mail = mail
            self.status = status
            self.currentIssue = currentIssue
            self.trainingStage = trainingStage
            self.courseLesson = courseLesson
        else:
            # parse from json

            # mandatory fields
            self.id = userDetails['id']
            self.name = userDetails['name']

            # non mandatory fields - set default values:
            self.mail = ''
            self.status = ''
            self.currentIssue = ''
            self.trainingStage = ''


            # non mandatory values - set only if existing
            if ('mail' in userDetails):
                self.mail = userDetails['mail']

            if ('status' in userDetails):
                self.status = userDetails['status']

            if ('currentIssue' in userDetails):    
                self.currentIssue = userDetails['currentIssue']
            
            if ('trainingStage' in userDetails): 
                self.trainingStage = userDetails['trainingStage']

            if ('courseLesson' in userDetails):
                self.courseLesson = userDetails['courseLesson']

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
    def __init__(self, id = None, issueId = None, type = None, name  = None, description = None, url = None, additionalInfoDetails = None):
        if (additionalInfoDetails is None):
            self.id = id
            self.issueId = issueId
            self.type = type
            self.name = name
            self.description = description
            self.url = url

        else:
            # parse from json

            # mandatory fields
            self.id = additionalInfoDetails['id']
            self.name = additionalInfoDetails['name']
            self.issueId = additionalInfoDetails['issueId']
            self.type = additionalInfoDetails['type']

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
            self.maxAttributesDetla = None
                
            if (minAttributesDelta is not None):
                self.minAttributesDelta = minAttributesDelta.copy()

            if (maxAttributesDelta is not None):
                self.minAttributesDelta = maxAttributesDelta.copy()

        else:
            #parse from list 
            # mandatory fields
            self.minText = questionRangeDetails['min']['idx']
            self.maxText = questionRangeDetails['max']['idx']
            self.tangeValue = questionRangeDetails['rangeValue']
            self.minAttributesDelta = None
            self.maxAttributesDetla = None

            if ('attributes' in questionRangeDetails['min']):
                if (questionRangeDetails['min']['attributes'].len > 0):
                    self.minAttributesDelta = questionRangeDetails['min']['attributes'].copy()
            
            if ('attributes' in questionRangeDetails['max']):
                if (questionRangeDetails['max']['attributes'].len > 0):            
                    self.maxAttributesDelta = questionRangeDetails['max']['attributes'].copy()

class questionData:
    def __init__(self, id = None, text = None, stage = None, type = None, options = None, range = None, questionDetails = None):
        if (questionDetails is None):
            self.id = id
            self.text = text
            self.stage = stage
            self.type = type
            self.options = None
            self.range = None

            if (options is not None):
                self.options = options.copy()

            if (range is not None):
                self.range = range.copy()
        else:
            #parse from list
            # mandatory fields
            self.id = questionDetails['id']
            self.text = questionDetails['text']
            self.stage = questionDetails['stage']
            self.type = questionDetails['type']
            self.options = None
            self.range = None

            if ('options' in questionDetails):
                if (questionDetails['options'].len > 0):
                    self.options = []

                    #create options list
                    for currOption in questionDetails['options']:
                        self.options.append(questionOptionDetails = questionOptionData(currOption))

            if ('range' in questionDetails):
                if (questionDetails['range'].len > 0):
                    self.range = questionRangeData(questionRangeDetails = questionDetails['range'])