// Google Sign-In for server-side apps
// https://developers.google.com/identity/sign-in/web/server-side-flow

// GGL Step 1: Create a client ID and client secret
// GGL Step 2: Add a button to the login page
// GGL Step 3: Include jQuery and Google platform library
// GGL Step 4: Initialize the GoogleAuth object


// GGL Steps 5 & 6
$('.loginBtn--google').click(function() {
  // GGL Step 6: Send authorization code to the server
  function signInCallback(authResult){
    // Check one-time-auth-code is present
    if (authResult['code']){
      // Hide login buttons now that the user is authorized
      $('#buttons').attr('style', 'display: none');
      // Send one-time-auth-code to the server
      $.ajax({
        // Set method and route, passing the anti-forgery-state-token
        type: 'POST',
        url: `/gconnect?state_token=${state_token}`,
        // Always include this header in every AJAX request, to protect against CSRF attacks.
        headers: {
        'X-Requested-With': 'XMLHttpRequest'
        },
        // octet-stream: arbitrary, binary stream of data
        contentType: 'application/octet-stream; charset=utf-8',
        // On 200 response from server
        success:function(result){
          if (result) {
            // Handle or verify server response.
            $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
            // Redirect user
            setTimeout(function() {
              window.location.href = "/";
            }, 2000);
          } else {
              $('#result').html('Failed to make a server-side call. Check your configuration and console.');
            }
        },
        // don't process reponse into a string
        processData:false,
        // data to send to server
        data:authResult['code']
      });
    } else { // authResult['error'] present
        console.log('There was an error: ' + authResult['error']);
      }
  }
  // GGL Step 5: Sign in the user
  // user grants access on google's sign-in click (client recieves access-token, one-time-auth-code)
  // call signInCallback({"code":"one-time-auth-code")
  auth2.grantOfflineAccess().then(signInCallback);
});

// GGL Step 7: Exchange the authorization code for an access token on server-side
