var NG_DASH_API_ROOT = "http://localhost:1572/_ah/api";
var clientId = '731555738015-jstpm0j9hcsv266fnj098q897n3bcifb.apps.googleusercontent.com';
var scopes = 'https://www.googleapis.com/auth/userinfo.email';


// prod
NG_DASH_API_ROOT = "https://ng-dash.appspot.com/_ah/api";
clientId = '731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com';


function checkAuth() {
  gapi.auth.authorize({
      client_id: clientId,
      scope: scopes,
      immediate: true
    }, handleAuthResult);
}

function handleAuthResult(authResult) {
  console.log("handleAuthResult");
  if (authResult && !authResult.error) {
    console.log("successful auth");
    onAuthSuccess();
  } else {
    console.log("calling authorize");
    gapi.auth.authorize({
        client_id: clientId,
        scope: scopes,
        immediate: false
        }, onAuthSuccess);
  }
}



var gapiLoaded = false;

var onGapiLoad = function onGapiLoad() {
  gapiLoaded = true;
};


var script = document.createElement("script");
script.src = "https://apis.google.com/js/client.js?onload=onGapiLoad";
script.async = true;
document.body.appendChild(script);


function onNgDashApiLoaded() {
  console.log("Loaded API. Now fetching runs.");
  gapi.client.ngdash.run.listRuns({}).execute(function(resp) {
    if (!resp.code) {
      console.log("Fetched runs.");
      console.log(resp.items);
    } else {
      console.error("Error loading runs");
      console.error(resp.code);
    }
  });
}


function onAuthSuccess() {
  gapi.client.load('ngdash', 'v0.1', onNgDashApiLoaded, NG_DASH_API_ROOT);
}

function onGapiLoad2() {
  console.log("GAPI loaded. Now loading API.");
  checkAuth();
}


if (gapiLoaded) {
  onGapiLoad2();
} else {
  onGapiLoad = onGapiLoad2;
}
