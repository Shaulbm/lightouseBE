// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import {fetch} from 'wix-fetch'; 
import wixUsers from 'wix-users';
import {session} from 'wix-storage'

$w.onReady (async function ()
{
	
	$w("#footer1").style.backgroundColor = "rgba(0, 0, 0, 1.0)";
	$w("#footer1").children.forEach((item, i) =>{item.collapse()});
	await updateUserData();
	await $w("#loadingBox1").hide();
	await $w("#loadingBox2").hide();
});

export async function updateUserData()
{
   const userData = await fetchUserData();

	if (userData.currentIssue == "")
	{
		$w('#issueName').text = "Seriously?";
		$w('#issueDescription').text = "Nothing is bothering you? Please go the Discover page and do some work :)";
	}

	const issueData = await fetchIssueData(userData.currentIssue);

	if (issueData)
	{
		$w('#issueName').text = issueData.name;
		$w('#issueDescription').text = issueData.description;
	} 

	const trainingStageData = await fetchTrainingData(userData.currentIssue, userData.trainingStage);

	if (trainingStageData)
	{
		$w('#currentChallengeShortDesc').text = trainingStageData.shortDescription;
		$w('#currentChallengeFullDesc').text = trainingStageData.descriptionInDetails;
	}
	else
	{
		$w('#currentChallengeShortDesc').text = "No active training";
		$w('#currentChallengeFullDesc').text = "can't find any training data on this issue";
	}

	const courseLessonData = await fetchCourseData(userData.currentIssue, userData.courseLesson);

	if (courseLessonData)
	{
		$w('#currentLessonShortDesc').text = courseLessonData.shortDescription;
		//$w('#lessonVideoURL').text = courseLessonData.videoURL;
		let str = courseLessonData.videoURL;
		let newUrl = "http://i.ytimg.com/vi/" + str.substr(str.indexOf("?v=")+3, str.length-1) + "/hqdefault.jpg";
		$w("#videoSnapshot").src = newUrl;
		session.setItem('currentLessonVideoURL', courseLessonData.videoURL);
	}
	else
	{
		$w('#currentLessonShortDesc').text = "No course data";
		//$w('#lessonVideoURL').text = "can't find any course data on this issue";
	}

	const trainingMapData = await fetchTrainingMapData(userData.currentIssue, userData.trainingStage);
	if (trainingMapData)
	{
		console.log ("past stage is " + JSON.stringify(trainingMapData.pastStages));

		if (trainingMapData.pastStages.length > 0)
		{
			console.log ("past 0 "+ trainingMapData.pastStages[0]);
			$w('#activityHistory1StepsAgo').text = trainingMapData.pastStages[0].shortDescription;
		}

		if (trainingMapData.pastStages.length > 1)
		{
			console.log ("past 1 "+ trainingMapData.pastStages[1]);
			$w('#activityHistory2StepsAgo').text = trainingMapData.pastStages[1].shortDescription;
		}

		if (trainingMapData.futureStages.length > 0)
		{
			console.log ("future 0 " + trainingMapData.futureStages[0]);
			$w('#activityFuture1StepsAhead').text = trainingMapData.futureStages[0].shortDescription;
		}

		if (trainingMapData.futureStages.length > 1)
		{
			console.log ("future 1 "+ trainingMapData.futureStages[1]);
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

export async function fetchIssueData(issueId)
{
	const url = "https://52.30.104.65:8000/issue?id=" + issueId;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export async function nextChallenge_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	await $w("#loadingBox2").show();
	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
		console.log("user id is: " + user.id + " user email is: " + userMail)
	}
	const url = "https://52.30.104.65:8000/setUserNextTrainingStage?userName=" + userMail;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();

		await updateUserData();
		await $w("#loadingBox2").hide();
        return result;
    }
	await $w("#loadingBox2").hide();
    return {};
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export async function nextLesson_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	await $w("#loadingBox1").show();
	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
		console.log("user id is: " + user.id + " user email is: " + userMail)
	}
	const url = "https://52.30.104.65:8000/setUserNextCourseLesson?userName=" + userMail;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();

		await updateUserData();
		await $w("#loadingBox1").hide();
        return result;
    }
	await $w("#loadingBox1").hide();
    return {};
}