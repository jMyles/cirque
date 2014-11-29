

import sys, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_plugin.settings'

sys.path.insert(0, '../')

from hendrix.deploy.base import HendrixDeploy
from client_protocol import CJDNSAdminClient
import django
from hendrix.contrib.async.resources import MessageResource,\
    MessageHandlerProtocol
from hendrix.contrib.async.messaging import send_json_message, hxdispatcher
from twisted.internet.task import LoopingCall
from hendrix.resources import DjangoStaticResource, NamedResource
import json
from txsockjs.factory import SockJSResource
from twisted.internet.protocol import Factory

from django_plugin.models import CJDNSRoute




class CirqueDeploy(HendrixDeploy):
    pass


class CirqueHendrixListener(MessageHandlerProtocol):

    def dataReceived(self, data):
        print "Received %s" % data
        return MessageHandlerProtocol.dataReceived(self, data)


def f(data_dict):
    
    routes = []
    
    for route_dict in data_dict['routingTable']:
        CJDNSRoute.objects.create(**route_dict)  # Obviously this is non-optimal.  TODO: Fix.

class CirqueCJDNSListener(CJDNSAdminClient):

    keepalive = True

    def connection_complete(self):
        print self.engage('NodeStore_nodeForAddr')
        peer_deferred = self.engage('InterfaceController_peerStats')
        print self.engage('AdminLog_subscribe')
        print self.engage('NodeStore_dumpTable', page=1, callbacks=[f])

    def dispatch_result(self, inquiry):
        print "Sending %s" % inquiry
#         send_json_message('cjdns_announce', inquiry.result)

    def dispatch_log_event(self, data_dict):
        # print "Sending log event %s" % data_dict
        send_json_message('log-debug', data_dict)


deploy = CirqueDeploy(options={'settings':'django_plugin.settings', 'HTTP_PORT': 8010})

CirqueResource = NamedResource('messages')
CirqueResource.putChild(
    'cirque_websocket',
    SockJSResource(Factory.forProtocol(CirqueHendrixListener))
)

deploy.resources.append(CirqueResource)


reactor = deploy.reactor

cjdns_sesh = CirqueCJDNSListener('127.0.0.1', 11234, "pkdf8rnwtsd0dn1k3289bh9yq0855cp")

static_resource = DjangoStaticResource("/home/justin/git/cirque/app", "static")
deploy.resources.append(static_resource)


reactor.listenUDP(5500, cjdns_sesh)

django.setup()
deploy.run()
