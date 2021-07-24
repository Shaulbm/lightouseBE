// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import {fetch} from 'wix-fetch'; 
import wixUsers from 'wix-users';
import {session} from 'wix-storage'

let likeLessonPressed = false;
let dislikeLessonPressed = false;
let likeChallengePressed = false;
let dislikeChallengePressed = false;

$w.onReady (async function ()
{
	$w("#processBox").hide();
	$w("#processImage").hide();
	$w("#processDownload").hide();
	
	await updateUserData();

	$w("#loadingBox1").hide();
	$w("#loadingBox2").hide();
});

export async function updateUserData()
{
   const userData = await fetchUserData();

	console.log ("after fetch data");

	if (userData.currentIssue == "")
	{
		$w('#issueName').text = "Seriously?";
		$w('#issueDescription').text = "Nothing is bothering you? Please go the Discover page and do some work :)";
	}

	console.log ("after user response");

	const issueData = await fetchIssueData(userData.currentIssue);

	console.log ("got issue data");

	if (issueData)
	{
		$w('#issueName').text = issueData.name;
		$w('#issueDescription').text = issueData.description;
	} 

	const issueAdditionalDataList = await fetchIssueAdditionalData(issueData.id);
	let processImageUrl = "";

	console.log ("got issue additional data");

	if (issueAdditionalDataList)
	{
		console.log ("issueAddtionalData has values");
		// Search for the process
		for (let currIssueDataIdx = 0; currIssueDataIdx < issueAdditionalDataList.length; currIssueDataIdx++)
		{
			if (issueAdditionalDataList[currIssueDataIdx].infoType == "process")
			{
				console.log ("process image url was set");
				processImageUrl = issueAdditionalDataList[currIssueDataIdx].url;
				break;
			}	
		}
	}

	if (processImageUrl != "")
	{
		$w("#processImage").src = processImageUrl;
		$w("#processDownload").link = processImageUrl;

		$w("#processBox").show();
		$w("#processImage").show();
		$w("#processDownload").show();
	}
	else
	{
		// No process URL - hide the process data
		$w("#processBox").hide();
		$w("#processImage").hide();
		$w("#processDownload").hide();
	}

	console.log ("before training data");

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

	console.log ("before course data");

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

	console.log ("before map data");

	const trainingMapData = await fetchTrainingMapData(userData.currentIssue, userData.trainingStage);
	if (trainingMapData)
	{
		console.log ("past stage is " + JSON.stringify(trainingMapData.pastStages));

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
 *	 @param {$w.MouseEvent} 
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
		console.log ("got user details response");
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

export async function fetchIssueAdditionalData(issueId)
{
	const url = "https://52.30.104.65:8000/additionalIssueDetails?issueId=" + issueId;
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

	//Zero like/dislike
	$w("#likeChallenge").style.borderWidth = "1px";
	$w("#likeChallenge").style.borderColor = "#57BBBF";
	$w("#dislikeChallenge").style.borderWidth = "1px";
	$w("#dislikeChallenge").style.borderColor = "#57BBBF";
	likeChallengePressed = false;
	dislikeChallengePressed = false;

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

	//Zero like/dislike
	$w("#likeLesson").style.borderWidth = "1px";
	$w("#likeLesson").style.borderColor = "#57BBBF";
	$w("#dislikeLesson").style.borderWidth = "1px";
	$w("#dislikeLesson").style.borderColor = "#57BBBF";
	likeLessonPressed = false;
	dislikeLessonPressed = false;

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

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function likeLesson_click(event)
{
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	
	if (likeLessonPressed)
	{
		console.log ("Like Lesson was true");
		likeLessonPressed = false;
		// like lesson remove border
		$w("#likeLesson").style.borderWidth = "1px";
		$w("#likeLesson").style.borderColor = "#57BBBF";

	}
	else
	{
		console.log ("Like Lesson was false");
		likeLessonPressed = true;
		dislikeChallengePressed = false;
		// like lesson show border
		$w("#likeLesson").style.borderWidth = "2px";
		$w("#likeLesson").style.borderColor = "#E9DB89";

		// verify dislike lesson remove border
		$w("#dislikeLesson").style.borderWidth = "1px";
		$w("#dislikeLesson").style.borderColor = "#57BBBF";
	}
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function dislikeLesson_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	
	if (dislikeLessonPressed)
	{
		console.log ("Dislike Lesson was true");
		dislikeLessonPressed = false;
		// like lesson remove border
		$w("#dislikeLesson").style.borderWidth = "1px";
		$w("#dislikeLesson").style.borderColor = "#57BBBF";

	}
	else
	{
		console.log ("Dislike Lesson was false");
		dislikeLessonPressed = true;
		likeChallengePressed = false;
		// like lesson show border
		$w("#dislikeLesson").style.borderWidth = "2px";
		$w("#dislikeLesson").style.borderColor = "#E9DB89";

		// verify dislike lesson remove border
		$w("#likeLesson").style.borderWidth = "1px";
		$w("#likeLesson").style.borderColor = "#57BBBF";
	}

}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function likeChallenge_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 

	if (likeChallengePressed)
	{
		console.log ("Like challenge was true");
		likeChallengePressed = false;
		// like lesson remove border
		$w("#likeChallenge").style.borderWidth = "1px";
		$w("#likeChallenge").style.borderColor = "#57BBBF";

	}
	else
	{
		console.log ("Like challenge was false");
		likeChallengePressed = true;
		dislikeChallengePressed = false;
		// like lesson show border
		$w("#likeChallenge").style.borderWidth = "2px";
		$w("#likeChallenge").style.borderColor = "#E9DB89";

		// verify dislike lesson remove border
		$w("#dislikeChallenge").style.borderWidth = "1px";
		$w("#dislikeChallenge").style.borderColor = "#57BBBF";
	}
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function dislikeChallenge_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	if (dislikeChallengePressed)
	{
		console.log ("Dislike challenge was true");
		dislikeChallengePressed = false;
		// like lesson remove border
		$w("#dislikeChallenge").style.borderWidth = "1px";
		$w("#dislikeChallenge").style.borderColor = "#57BBBF";

	}
	else
	{
		console.log ("Dislike Challenge was false");
		dislikeChallengePressed = true;
		likeChallengePressed = false;
		// like lesson show border
		$w("#dislikeChallenge").style.borderWidth = "2px";
		$w("#dislikeChallenge").style.borderColor = "#E9DB89";

		// verify dislike lesson remove border
		$w("#likeChallenge").style.borderWidth = "1px";
		$w("#likeChallenge").style.borderColor = "#57BBBF";
	}
}