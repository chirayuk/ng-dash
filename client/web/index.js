"use strict";

var NG_DASH_API_ROOT = "https://ng-dash.appspot.com/_ah/api";
var clientId = '731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com';
var scopes = 'https://www.googleapis.com/auth/userinfo.email';

var G = {
  loading: true,
  runs: [],
  singleRunSha: null,
  errorMsg: "",
  asyncQueue: [],
  requestDigest: false,
  digest: null
};

var ngDashApi = null;

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
  ngDashApi = gapi.client.ngdash;
}


function onGapiLoad() {
  gapi.client.load('ngdash', 'v0.1', onNgDashApiLoaded, NG_DASH_API_ROOT);
}


// Lazy man's autodigest/async queue. :(
function onFrame() {
  if (ngDashApi && G.asyncQueue.length > 0) {
    G.asyncQueue.forEach(function(fn) {fn();});
    G.asyncQueue = [];
    G.requestDigest = true;
  }
  if (G.requestDigest && G.digest) {
    G.requestDigest = false;
    G.digest();
  }
  window.requestAnimationFrame(onFrame);
}

onFrame();


// Angular Stuff.

var module = angular.module('ngDash', ['ngRoute']);

module.controller('MainController', ['$scope', function MainController($scope) {
    $scope.G = G;
    G.digest = $scope.$digest.bind($scope);
}]);


function onRunsLoaded(resp) {
  G.loading = false;
  G.requestDigest = true;
  if (!resp.code) {
    if (resp.items) {
      G.runs = resp.items;
      processRuns(G.runs);
    } else {
      G.runs = [];
      G.errorMsg = "Alas! We couldn't find any results for you.";
    }
  } else {
    console.error(resp.code);
    G.errorMsg = "Error loading runs: " + resp.code;
  }
}


function loadRuns(commitSha) {
  G.loading = true;
  G.singleRunSha = commitSha;
  G.runs = [];
  G.errorMsg = null;
  if (commitSha != null) {
    ngDashApi.run.getRunBySha({commit_sha: commitSha}).execute(onRunsLoaded);
  } else {
    ngDashApi.run.listRuns({}).execute(onRunsLoaded);
  }
}


module.controller('AllRunsController', [function AllRunsController() {
  G.asyncQueue.push(loadRuns);
}]);


module.controller('SingleRunController', ['$routeParams',
              function SingleRunController($routeParams) {
  var commitSha = $routeParams.commitSha;
  G.asyncQueue.push(function() {
    loadRuns(commitSha);
  });
}]);



module.directive('run', function() {
  return {
    scope: {
      run: "="
    },
    templateUrl: '/run.html'
  };
});

module.directive('runData', function() {
  return {
    scope: {
      data: "=runData"
    },
    templateUrl: '/runData.html'
  };
});

module.directive('nameValues', function() {
  return {
    scope: {
      data: "=nameValues",
    },
    templateUrl: '/nameValues.html'
  };
});

module.filter('utcTimestampToLocalDate', function() {
  return function timestampToLocalString(timestamp) {
    return new Date(timestamp * 1000);
  };
});


module.config(['$routeProvider', '$locationProvider',
       function($routeProvider,   $locationProvider) {
  $locationProvider.html5Mode(true);
  $routeProvider.
    when('/', {
      templateUrl: '/overview.html',
    }).
    when('/all', {
      controller: 'AllRunsController',
      templateUrl: '/all.html',
    }).
    when('/commit/:commitSha', {
      controller: 'SingleRunController',
      templateUrl: '/commit.html',
    }).
    otherwise({
      redirectTo: '/all'
    });
}]);
