// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import {fetch} from 'wix-fetch'; 
import wixUsers from 'wix-users';
import {session} from 'wix-storage'

$w.onReady (async function ()
{
	await updateUserData();
});

export async function updateUserData()
{
   const userData = await fetchUserData();
    if (userData){
		$w('#userNameText').text = userData.name;
	 	$w('#userStatusText').text = "USER STATUS: " + userData.status;
    }

	const trainingStageData = await fetchTrainingData(userData.currentIssue, userData.trainingStage);

	if (trainingStageData)
	{
		$w('#currentChallengeShortDesc').text = trainingStageData.shortDescription;
		$w('#currentChallengeFullDesc').text = trainingStageData.descriptionInDetails;
	}

	const courseLessonData = await fetchCourseData(userData.currentIssue, userData.courseLesson);

	if (courseLessonData)
	{
		$w('#currentLessonShortDesc').text = courseLessonData.shortDescription;
		$w('#lessonVideoURL').text = courseLessonData.videoURL;
		session.setItem('currentLessonVideoURL', courseLessonData.videoURL);
	}

	const trainingMapData = await fetchTrainingMapData(userData.currentIssue, userData.trainingStage);
	if (trainingMapData)
	{
		if (trainingMapData.pastStages.length > 0)
		{
			$w('#activityHistory1StepsAgo').text = trainingMapData.pastStages[0].shortDescription;
		}

		if (trainingMapData.pastStages.length > 1)
		{
			$w('#activityHistory2StepsAgo').text = trainingMapData.pastStages[1].shortDescription;
		}

		if (trainingMapData.futureStages.length > 0)
		{
			$w('#activityFuture1StepsAhead').text = trainingMapData.futureStages[0].shortDescription;
		}

		if (trainingMapData.futureStages.length > 1)
		{
			$w('#activityFuture2StepsAhead').text = trainingMapData.futureStages[1].shortDescription;
		}
		
		$w('#activityCurrentStep').text = trainingMapData.currentStage.shortDescription;		
	}
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export async function fetchUserData()
{
    //const url = "https://52.30.104.65:8000/registerUser?user=" + $w('#input4').value;

	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
		console.log("user id is: " + user.id + " user email is: " + userMail)
	}
	const url = "https://52.30.104.65:8000/registerUser?user=" + userMail;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
 }

export async function fetchTrainingData(issueId, trainingStage)
{
	//console.log("issue id is: " + user.id + " user email is: " + userMail)
	const url = "https://52.30.104.65:8000/getTrainingStage?issueId=" + issueId + "&stage=" + trainingStage;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
 }

export async function fetchCourseData(issueId, courseLesson)
{
	//console.log("issue id is: " + user.id + " user email is: " + userMail)
	const url = "https://52.30.104.65:8000/getCourseLesson?issueId=" + issueId + "&lesson=" + courseLesson;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
 }

export async function fetchTrainingMapData(issueId, currentStage)
{
	const url = "https://52.30.104.65:8000/trainingMap?issueId=" + issueId + "&stage=" + currentStage;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
}

export async function button5_click(event) {
 }