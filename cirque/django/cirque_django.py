from hendrix.deploy import HendrixDeploy
from cirque.client_protocol import CJDNSAdminClient
import django
from hendrix.contrib.async.resources import MessageResource
from hendrix.contrib.async.messaging import send_json_message, hxdispatcher
from twisted.internet.task import LoopingCall
from hendrix.resources import DjangoStaticResource
import json

class CirqueDeploy(HendrixDeploy):
    pass

class CirqueListener(CJDNSAdminClient):

    keepalive = True

    def connection_complete(self):
        print "Asking whoami"
        print self.engage('NodeStore_nodeForAddr')
        print self.engage('InterfaceController_peerStats')
        print self.engage('AdminLog_subscribe')

    def dispatch_result(self, inquiry):
        print "Sending %s" % inquiry.result
#         send_json_message('cjdns_announce', inquiry.result)

    def dispatch_log_event(self, data_dict):
        print "Sending log event %s" % data_dict
        send_json_message('cjdns_announce', data_dict)


deploy = CirqueDeploy(options={'settings':'settings'})
deploy.resources.append(MessageResource)
reactor = deploy.reactor

cjdns_sesh = CirqueListener('127.0.0.1', 11234, "pkdf8rnwtsd0dn1k3289bh9yq0855cp")

static_resource = DjangoStaticResource("app", "static")
deploy.resources.append(static_resource)


reactor.listenUDP(5500, cjdns_sesh)

django.setup()
deploy.run()


