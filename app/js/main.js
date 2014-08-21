angular.module('cirque', ['ui.bootstrap', 'ngGrid']);



subscribe_to_channel = function(channel_address){
var data = {
hx_subscribe:channel_address,
};
// console.log(data)
window.sock.send(JSON.stringify(data));
}

 window.sock.onopen = function() {
     console.log('open');
     subscribe_to_channel('cjdns_announce');
 };
 window.sock.onclose = function() {
     console.log('close');
 };


function Table($scope) {

  $scope.gridOptions = { data: 'myData',
        enableColumnResize: true,
        enableColumnReordering: true,
        headerRowHeight: 44,
        enablePaging: true,
        columnDefs: [{ field: "ip", width: 200},
                    { field: "parentChildLabel", width: 200 },
                    { field: "reach", width: 200 },
                    { field: "encodingScheme", width: 200 }]
   };
  }

function Peers($scope) {
  $scope.peers = []
}

function Logs($scope) {
    $scope.log_entries = ['Sample log entry.']
    sock.onmessage = function(e) {
          var array = $.map(JSON.parse(e.data).message, function(value, index) {
            return [value];
        });
            $scope.log_entries.push({msg: array});
        };
}

function Alert($scope) {
  $scope.alerts = [
    { type: 'danger', msg: 'Oh snap! Change a few things up and try submitting again.' },
    { type: 'success', msg: 'Well done! You successfully read this important alert message.' }
  ];

  $scope.addAlert = function() {
    $scope.alerts.push({msg: 'WHY?!?!??!?!'});
  };

  $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };

}

var Tabs = function ($scope) {
  $scope.tabs = [
    { title:'Dynamic Title 1', content:'Dynamic content 1' },
    { title:'Dynamic Title 2', content:'Dynamic content 2', disabled: true }
  ];

  $scope.alertMe = function() {
    setTimeout(function() {
      alert('You\'ve selected the alert tab!');
    });
  };
};
