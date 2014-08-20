from hendrix.deploy import HendrixDeploy
from cirque.client_protocol import CJDNSAdminClient
import django
from hendrix.contrib.async.resources import MessageResource
from hendrix.contrib.async.messaging import send_json_message, hxdispatcher
from twisted.internet.task import LoopingCall



class CirqueDeploy(HendrixDeploy):
    pass

class CirqueListener(CJDNSAdminClient):

    keepalive = True

    def connection_complete(self):
        print "Asking whoami"
        print self.engage('NodeStore_nodeForAddr')
        print self.engage('InterfaceController_peerStats')

        def hi():
            send_json_message('cjdns_announce', self.get_node_information())

        hello = LoopingCall(hi)
        hello.start(1)



deploy = CirqueDeploy(options={'settings':'settings'})
deploy.resources.append(MessageResource)
reactor = deploy.reactor

cjdns_sesh = CirqueListener('127.0.0.1', 11234, "pkdf8rnwtsd0dn1k3289bh9yq0855cp")

reactor.listenUDP(5500, cjdns_sesh)

django.setup()
deploy.run()


