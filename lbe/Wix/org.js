// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import {fetch} from 'wix-fetch'; 
import wixUsers from 'wix-users';

$w.onReady(async function () {
	// Write your JavaScript here

	// To select an element by ID use: $w("#elementID")

	// Click "Preview" to run your code
});

export async function fillOrgData()
{
	const orgData = await fetchOrgData();
	if (orgData.length > 0)
	{
		console.log ("bigger than 0");
		let orgDataStr = "";
		for (let currentOrgMemeberIdx = 0; currentOrgMemeberIdx < orgData.length; currentOrgMemeberIdx++)
		{
			orgDataStr += orgData[currentOrgMemeberIdx].name + "\n";
		}
		$w('#subordinatesChart').text = orgDataStr;
	}
}

export async function fetchOrgData()
{
	let user = wixUsers.currentUser;
	let userMail = "Undefined";

	if (user.loggedIn)
	{
		userMail = await user.getEmail();
		console.log("user id is: " + user.id + " user email is: " + userMail)

		// for now debug
		userMail = $w("#userName").value;
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

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */
export async function fetch_click(event) {
	// This function was added from the Properties & Events panel. To learn more, visit http://wix.to/UcBnC-4
	// Add your code for this event here:
		await fillOrgData(); 
}