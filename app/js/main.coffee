angular.module('cirque', ['ui.bootstrap', 'ngGrid'])

window.sock = new SockJS('http://localhost:8080/messages/cirque_websocket')

subscribe_to_channel = (channel_address) ->
  data = {
    hx_subscribe:channel_address,
  };

  window.sock.send(JSON.stringify(data));

window.sock.onopen = () ->
  subscribe_to_channel("log-debug")

window.sock.onmessage = (payload) ->
    dataObj = JSON.parse(payload.data)

    if dataObj.hasOwnProperty('setup_connection')
      console.log('Connection established.', dataObj)

    if dataObj.subject_id == "log-debug"
      logScope.consume_log(dataObj.message)

window.Peers = ($scope) ->
  $scope.peers = []

window.Logs = ($scope) ->
  window.logScope = $scope
  $scope.log_entries = []

  $scope.gridOptions = {data: 'log_entries'}

  $scope.consume_log = (logObj) ->
      console.log("Adding another row!")
      $scope.log_entries.push(logObj)



window.Alert = ($scope) ->
    $scope.alerts = []

window.Tabs = ($scope) ->
    $scope.tabs = []

window.Table = ($scope) ->
    $scope.gridOptions = {}
