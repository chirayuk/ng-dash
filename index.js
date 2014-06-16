"use strict";

var NG_DASH_API_ROOT = "https://ng-dash.appspot.com/_ah/api";
var clientId = '731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com';
var scopes = 'https://www.googleapis.com/auth/userinfo.email';

var G = {
  runs: [],
  errorMsg: ""
};

function defaultCompare(a, b) {
  return (a == b) ? 0 : (a < b) ? -1 : 1;
}


function flattenNameValues(data, result, prefix) {
  result = result ? result : [];
  prefix = prefix ? prefix : "";
  Object.keys(data).forEach(function(name) {
    var value = data[name];
    if (value.__proto__ === Object.prototype) {
      flattenNameValues(value, result, prefix + name + ".");
    } else {
      result.push({name: prefix + name, value: value});
    }
  });
  result.sort(function(a, b) {
    return defaultCompare(a.name, b.name);
  });
  return result;
}


function processRunData(data) {
  data.dimensions = flattenNameValues(JSON.parse(data.dimensions_json));
  delete data.dimensions_json;
  data.metrics = flattenNameValues(JSON.parse(data.metrics_json));
  delete data.metrics_json;
  if (data.children) {
    data.children.forEach(processRunData);
  } else {
    data.children = [];
  }
}

function processRun(run) {
  if (run.data) {
    processRunData(run.data);
  }
}


function processRuns(runs) {
  runs.sort(function compareCreationTimestamp(a, b) {
    return b.creation_timestamp - a.creation_timestamp;
  });
  runs.forEach(processRun);
}


function onNgDashApiLoaded() {
  gapi.client.ngdash.run.listRuns({}).execute(function(resp) {
    if (!resp.code) {
      G.runs = resp.items;
      processRuns(G.runs);
    } else {
      console.error(resp.code);
      G.errorMsg = "Error loading runs: " + resp.code;
    }
  });
}


function onGapiLoad() {
  gapi.client.load('ngdash', 'v0.1', onNgDashApiLoaded, NG_DASH_API_ROOT);
}


var module = angular.module('ngDash', []);

module.controller('MainController', ['$scope', function ($scope) {
    $scope.G = G;
    function onFrame() {
      $scope.$digest();
      window.requestAnimationFrame(onFrame);
    };
    window.requestAnimationFrame(onFrame);
}]);

module.directive('run', function() {
  return {
    scope: { run: "=" },
    templateUrl: '/run.html'
  };
});

module.directive('runData', function() {
  return {
    scope: { data: "=runData" },
    templateUrl: '/runData.html'
  };
});

module.directive('nameValues', function() {
  return {
    scope: { data: "=nameValues", },
    templateUrl: '/nameValues.html'
  };
});

module.filter('utcTimestampToLocalDate', function() {
  return function utcTimestampToLocalDate(timestamp) {
    return new Date(timestamp * 1000);
  };
});
