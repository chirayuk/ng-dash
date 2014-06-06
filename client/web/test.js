var API_ROOT = "https://ng-codelab.appspot.com/_ah/api";

var gapiLoaded = false;

var onGapiLoad = function onGapiLoad() {
  gapiLoaded = true;
};


var script = document.createElement("script");
script.src = "https://apis.google.com/js/client.js?onload=onGapiLoad";
script.async = true;
document.body.appendChild(script);


function onApiLoaded() {
  console.log("Loaded API. Now fetching terms.");
  gapi.client.ngcodelab.term.listTerms({}).execute(function(resp) {
    if (!resp.code) {
      console.log("Fetched terms.");
      console.log(resp.items);
    } else {
      console.error("Error loading terms");
      console.error(resp.code);
    }
  });
}


function onGapiLoad2() {
  console.log("GAPI loaded. Now loading API.");
  gapi.client.load('ngcodelab', 'v1.0', onApiLoaded, API_ROOT);
}


if (gapiLoaded) {
  onGapiLoad2();
} else {
  onGapiLoad = onGapiLoad2;
}
