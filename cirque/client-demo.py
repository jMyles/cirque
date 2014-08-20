import publicToIp6
import adminTools as at
from coils import connect, TwistedSession

from twisted.internet import reactor


nodes = {
         'nice-name': ('some:ipv4:addr:ess0:0000:0000:0000:0000', 11234, 'thepassword')
        }

class WhoAmI(TwistedSession):

    def connection_complete(self):
        print "Asking whoami"
        print self.engage('NodeStore_nodeForAddr')
        print self.engage('InterfaceController_peerStats')



for node, node_settings in nodes.items():
    cjdns_sesh = WhoAmI(*node_settings)
    reactor.listenUDP(5500, cjdns_sesh)#interface='::')
    reactor.run()
