var NG_DASH_API_ROOT = "https://ng-dash.appspot.com/_ah/api";

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
      console.log(resp.runs);
    } else {
      console.error("Error loading runs");
      console.error(resp.code);
    }
  });
}


function onGapiLoad2() {
  console.log("GAPI loaded. Now loading API.");
  gapi.client.load('ngdash', 'v0.1', onNgDashApiLoaded, NG_DASH_API_ROOT);
}


if (gapiLoaded) {
  onGapiLoad2();
} else {
  onGapiLoad = onGapiLoad2;
}
