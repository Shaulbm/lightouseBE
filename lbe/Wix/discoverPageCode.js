// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import wixAnimations from 'wix-animations';
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

$w.onReady(function () {
	// Write your JavaScript here

	// To select an element by ID use: $w("#elementID")

	// Click "Preview" to run your code
});

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
	setUserIssueSelection(leadingIssue);
	changeSeletionText ("Want to improve in leading? let's train!")
}