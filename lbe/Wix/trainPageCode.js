// API Reference: https://www.wix.com/velo/reference/api-overview/introduction
// “Hello, World!” Example: https://learn-code.wix.com/en/article/1-hello-world
import {fetch} from 'wix-fetch'; 

$w.onReady(function () {
	// Write your JavaScript here

	// To select an element by ID use: $w("#elementID")

	// Click "Preview" to run your code
});

/**
 *	Adds an event handler that runs when the element is clicked.
 *	 @param {$w.MouseEvent} event
 */

 export async function fetchUserData(){
    const url = "https://52.30.104.65:8000/registerUser?user=" + $w('#input4').value;
    const httpResponse = await fetch(url,{'method':'POST'});
    if (httpResponse.ok){
        const result = await httpResponse.json();
        return result;
    }
    return {};
 }

export async function button5_click(event) {
    const userData = await fetchUserData();
    if (userData){
        $w("#userIdText").text = userData.id;
		$w('#userNameText').text = userData.name;
	 	$w('#userStatusText').text = userData.status;
    }
}