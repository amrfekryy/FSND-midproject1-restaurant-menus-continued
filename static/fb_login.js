// Facebook Login for the Web with the JS SDK
// https://developers.facebook.com/docs/facebook-login/web


// FB Step 1: Create app ID and app secret
// FB Step 2: Add a button to the login page

// FB Step: Check Login Status
// function statusChangeCallback(response) {
//   console.log('statusChangeCallback');
//   console.log(response);
//   if (response.status === 'connected') {
//     // Logged into app and Facebook.
//     testAPI();
//   } else {
//     // Not logged into app or unable to tell.
//     document.getElementById('status').innerHTML = 'Please log ' +
//       'into this app.';
//   }
// }

// This function is called when someone finishes with the Login
// Button.  See the onlogin handler attached to it in the sample
// code below.
// function checkLoginState() {
//   FB.getLoginStatus(function(response) {
//     statusChangeCallback(response);
//   });
// }

// FB Step 4: Initialize the FB Auth object
window.fbAsyncInit = function() {
  FB.init({
    appId      : '624700501334138',
    cookie     : true,  // enable cookies to allow the server to access the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v3.2' // The Graph API version to use for the call
  });
  // FB Step: Check Login Status
  // respone obj with status = connected/not_authorized/unknown
  // FB.getLoginStatus(function(response) {
  //   statusChangeCallback(response);
  // });
};
// FB Step 3: Load the SDK asynchronously
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "https://connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Here we run a very simple test of the Graph API after login is successful.  See statusChangeCallback() for when this call is made.
// function testAPI() {
//   console.log('Welcome!  Fetching your information.... ');
//   FB.api('/me', function(response) {
//     console.log('Successful login for: ' + response.name);
//     document.getElementById('status').innerHTML =
//       'Thanks for logging in, ' + response.name + '!';
//   });
// }


// FB Steps 5: Send token to the server
function sendTokenToServer() {
  // get the short-lived access token
  var access_token = FB.getAuthResponse()['accessToken'];
  // Check short-lived is present
  console.log(access_token)
  if (access_token) {
    // Hide login buttons now that the user is authorized
    $('#buttons').attr('style', 'display: none');
    // you can call fb api and get user data here
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
    });
    // Send one-time-auth-code to the server
    $.ajax({
      // Set method and route, passing the anti-forgery-state-token
      type: 'POST',
      url: `/fbconnect?state_token=${state_token}`,
      // don't process reponse into a string
      processData:false,
      // data to send to server
      data: access_token,
      // octet-stream: arbitrary, binary stream of data
      contentType: 'application/octet-stream; charset=utf-8',
      // On 200 response from server
      success: function(result) {
        // Handle or verify the server response if necessary.
        if (result) {
          // Handle or verify server response.
          $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
          // Redirect user
          setTimeout(function() {
            window.location.href = "/";
          }, 4000);
        } else {
            $('#result').html('Failed to make a server-side call. Check your configuration and console.');
          }
      }    
    });
  } else { // error in FB.getAuthResponse()['accessToken']
        console.log('Couldn\'t get short-lived token')
    }
};

$('.loginBtn--facebook').click(function() {
    FB.login(sendTokenToServer, {scope: 'email,public_profile', return_scopes: true})
  }
);

// FB Step 6: Exchange the authorization code for an access token on server-side

