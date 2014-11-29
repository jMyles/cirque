from django.http.response import HttpResponse

sockjs = '''
<!DOCTYPE html>
<!--[if lt IE 7]>      <html lang="en" ng-app="cirque" class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html lang="en" ng-app="cirque" class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html lang="en" ng-app="cirque" class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html lang="en" ng-app="cirque"> <!--<![endif]-->

 <head>
    <script src="static/js/jquery-2.1.1.min.js"></script>
    <script src="static/js/angular.js"></script>
    <script src="static/js/ui-bootstrap-tpls-0.11.0.min.js"></script>

    <script src="http://angular-ui.github.com/ng-grid/lib/ng-grid.debug.js"></script>
    <script src="http://cdn.sockjs.org/sockjs-0.3.min.js"></script>

    <script src="static/js/main.js"></script>
    <link href="static/css/bootstrap.min.css" rel="stylesheet">
    <link href="static/css/ui-grid.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="http://angular-ui.github.com/ng-grid/css/ng-grid.css" />
    </head>
  <body>

    <div ng-controller="Alert">
      <alert ng-repeat="alert in alerts" type="{{alert.type}}" close="closeAlert($index)">{{alert.msg}}</alert>
      <button class='btn btn-default' ng-click="addAlert()">Dont Press.</button>
    </div>

    <div ng-controller="Tabs">
      <tabset justified="true">
        <tab heading="Justified">

        </tab>
        <tab ng-controller="Peers" heading="Peers">
            <div ng-repeat="peer in peers">
                {{peer}}
            </div>
        </tab>
        <tab ng-controller="Logs" heading="Logs">

          <div class="gridStyle" ng-grid="gridOptions"></div>

        </tab>
      </tabset>
    </div>

    <div ng-controller="Table">

      <div class="gridStyle" ng-grid="gridOptions">
      </div>

    </div>

  </body>
</html>
'''


drf_demo_html = '''
<!DOCTYPE html>
<!--[if lt IE 7]>      <html lang="en" ng-app="cirque" class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html lang="en" ng-app="cirque" class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html lang="en" ng-app="cirque" class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html lang="en" ng-app="cirque"> <!--<![endif]-->

 <head>
    <script src="static/bower_components/angular/angular.js"></script>
    <script src="static/bower_components/angular-resource/angular-resource.js"></script>

    <script src="http://cdn.sockjs.org/sockjs-0.3.min.js"></script>

    <script src="static/js/cirque.js"></script>
    <script src="static/js/services.js"></script>

    <link rel="stylesheet" type="text/css" href="http://angular-ui.github.com/ng-grid/css/ng-grid.css" />
    </head>
  <body ng-app="cirque">
    BAHAHA CIRQUE
    <div ng-controller="UserCtrl">
      <ul>
      <div ng-repeat="user in users">
        <li>[[user.username]]</li>
      </div>
      </ul>
    </div>
    <div ng-controller="CJDNSRouteCtrl">
      <ul>
      <div ng-repeat="route in cjdnsRoutes">
        <li>[[route]]</li>
      </div>
      </ul>
    </div>
  </body>
</html>
'''


def main(request):
    return HttpResponse(sockjs)

def drf_demo(request):
    return HttpResponse(drf_demo_html)
