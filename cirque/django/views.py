from django.http.response import HttpResponse

sockjs = '''
<script src="http://cdn.sockjs.org/sockjs-0.3.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.2.22/angular.min.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script type="text/javascript">
 var sock = new SockJS('http://localhost:8080/messages/main');

subscribe_to_channel = function(channel_address){
var data = {
hx_subscribe:channel_address,
};
// console.log(data)
sock.send(JSON.stringify(data));
}

 sock.onopen = function() {
     console.log('open');
     subscribe_to_channel('cjdns_announce');
 };
 sock.onmessage = function(e) {
     $('#cjdns').append(e.data);
     console.log('message', e.data);
 };
 sock.onclose = function() {
     console.log('close');
 };
 </script>

 <!DOCTYPE html>
<html>

<body>

    <div id="cjdns"></div>

</body>
</html>

'''

def main(request):
    return HttpResponse(sockjs)