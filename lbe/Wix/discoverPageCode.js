// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import wixAnimations from 'wix-animations';
import wixWindow from 'wix-window';
import {fetch} from 'wix-fetch'; 
import wixUsers from 'wix-users';

let timeline1 = wixAnimations.timeline(  {
    "repeat": 1,
    "repeatDelay": 100,
    "yoyo": true
  });
let firstTimellineSettings = true;

const feedbackIssue = "ee728c15-c04a-4ecf-9c19-2a07ed37b65a"
const timeManagementIssue = "427e1335-5a0f-45a2-8c3f-3139f98452df";
const technicalManagerialBalanceIssue = "5631dfbc-65a7-431a-b08f-456058bbddf7";
const leadingIssue = "dabe54b7-47f3-4ed9-a02c-11868f3d94d1";

$w.onReady(async function () {
	// Write your JavaScript here

	// To select an element by ID use: $w("#elementID")
	hideIssuesOption();
	$w("#OpenDiscovery").show();

	await fillOrgData();
	// Click "Preview" to run your code
});


export function showIssuesOption ()
{
	$w("#feedback").show();
	$w("#timeManagement").show();
	$w("#technicalManagerialBalance").show();
	$w("#leading").show();
}

export function hideIssuesOption ()
{
	$w("#feedback").hide();
	$w("#timeManagement").hide();
	$w("#technicalManagerialBalance").hide();
	$w("#leading").hide();
}

export function changeSeletionText (selectionText)
{
	const myText = $w("#selectedIssue");
	myText.text = selectionText;

	if (firstTimellineSettings)
	{
		console.log("first time adding the animation to the timeline")

		timeline1.add(myText, {
				"easing": "easeOutQuad",
				"scale": .95,
				"duration": 250
		});

		firstTimellineSettings = false;
		console.log ("timeline - play");
		timeline1.play();
	}
	else
	{
		console.log ("timeline replay");
		timeline1.replay();
	}
}

export async function setUserIssueSelection(selectedIssueId)
{
	//setUserIssueId?userName=Test2&issueId=
	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
	}
	const url = "https://52.30.104.65:8000/setUserIssueId?userName=" + userMail + "&issueId=" + selectedIssueId;
	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
 }

export async function feedback_click_1(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 

	setUserIssueSelection(feedbackIssue);
	changeSeletionText ("Want to improve your feedback? let's train!")
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function timeManagement_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	setUserIssueSelection(timeManagementIssue);
	changeSeletionText ("Want to ace your time management? let's train!")
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function technicalManagerialBalance_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	setUserIssueSelection(technicalManagerialBalanceIssue);
	changeSeletionText ("Want to balance your focus? let's train!")
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export function leading_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	console.log("leading selected");
	setUserIssueSelection(leadingIssue);
	changeSeletionText ("Want to improve in leading? let's train!")
}

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export async function OpenDiscovery_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here: 
	await wixWindow.openLightbox("DiscoveryForm");

	changeSeletionText("are these issues bothering you?");

	$w("#OpenDiscovery").hide();
	showIssuesOption();
	$w("#selectedIssue").show();
}

export async function fillOrgData()
{
	const orgData = await fetchOrgData();
	if (orgData.length > 0)
	{
		let user = wixUsers.currentUser;
		const userMail = await user.getEmail()
		$w("#userSelection").show();

		console.log ("adding items to selection");
		let orgDataStr = "";
		let opts = $w("#userSelection").options;
		opts = [{"label": "Me", "value": userMail}];

		for (let currentOrgMemeberIdx = 0; currentOrgMemeberIdx < orgData.length; currentOrgMemeberIdx++)
		{
			opts.push({"label": orgData[currentOrgMemeberIdx].name, "value": orgData[currentOrgMemeberIdx].name});
		}

		$w("#userSelection").options = opts;
		//$w("#userSelection").selectedIndex = 0;
	}
	else
	{
		$w("#userSelection").hide();
	}
}

export async function fetchOrgData()
{
	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
		console.log("user id is: " + user.id + " user email is: " + userMail);
	}

	const url = "https://52.30.104.65:8000/usersUnder?userName=" + userMail;
	console.log("url to API:" + url);

	const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
		console.log ("got user details response"+ JSON.stringify(result));
        return result;
    }
    return {};
 }
