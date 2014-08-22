# You may redistribute this program and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue, QueueUnderflow
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
import bencoder
import pprint
import publicToIp6
import random
import string
import hashlib



BUFFER_SIZE = 69632
KEEPALIVE_INTERVAL_SECONDS = 2
SUPER_VERBOSE = False

log_file = open('admin_api_log', 'w')  # TODO: Better job of file naming here.


def random_string():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(10))


class CJDNSInquiry(object):
    '''
    A question-and-answer session between a client and the CJDNS Admin API
    about a particular topic.
    '''
    cookie = None

    default_args = {}
    call_args = {}

    finished = False
    result = None

    def __init__(self, client, function_name, **kwargs):
        self.client = client

        def send(data):
            '''
            This closure is a workaround because twisted won't let us
            connect in advance with ipv6
            '''
            def send_closure(data, host, port):
                return client.transport.write(data, (host, port))

            return send_closure(data, client.host, client.port)

        self.send = send

        self.function_name = function_name

        self.default_args = self.client.functions_available[function_name]

        for arg in self.default_args:
            if arg not in kwargs:
                # If the user didn't specify a value (ie, they didn't override the value for this kwarg)
                # then we'll assume they want the default.
                self.call_args[arg] = self.default_args[arg]
            else:
                # ...otherwise, we go with their kwarg.
                self.call_args[arg] = kwargs[arg]

    def __repr__(self):
        return "%s on %s" % (self.function_name, self.cookie)

    def request_cookie(self):
        '''
        Obtain a cookie
        '''
        if SUPER_VERBOSE:
            print "requested cookie for to run %s as %s" % (function_name, txid)

        txid = random_string()
        request = {'q': 'cookie', 'txid': txid}
        self.send(bencoder.encode(request))

        return txid

    def consume_cookie(self, data_dict, auto_call=True):
        self.cookie = data_dict['cookie']

        if auto_call:
            return self.call()



    def call(self):
        '''
        Call the function, passing self.arguments.
        Use self.cookie for auth if provided.
        '''
        password=self.client.password

        txid = random_string()

        pass_hash = hashlib.sha256(password + self.cookie).hexdigest()

        req = {
            'q': 'auth',
            'aq': self.function_name,
            'hash': pass_hash,
            'cookie': self.cookie,
            'args': self.call_args,
            'txid': txid
        }
        first_time_benc_req = bencoder.encode(req)
        req['hash'] = hashlib.sha256(first_time_benc_req).hexdigest()
        second_time_benc_req = bencoder.encode(req)

        if SUPER_VERBOSE:
            print "Calling function: %s" % req

        self.send(second_time_benc_req)

        return txid

    def receive_data(self, data_dict):
        if SUPER_VERBOSE:
            pprint.pprint("RESPONSE FOR %s is: %s" % (self.function_name, data_dict))


        if data_dict.has_key('peers'):
            result = data_dict['peers']
            self.close()

        if data_dict.get('txid'):
            if data_dict['txid'] in self.client.address_lookups.keys():
                ip = self.address_lookups[data_dict['txid']]
                print "%s has a route: %s" % (self.client.show_nice_name(ip), data_dict['result'])

        if data_dict.has_key('result'):
#             self.deal_with_result(data_dict['result'])  # TODO: This is a reasonable pattern.  Let's implement it.

            print "======GOT RESULT for %s======" % self.function_name


            if self.function_name == 'NodeStore_nodeForAddr':
                self.client.node_information = data_dict['result']
                self.result = data_dict['result']
                self.client.report_completed_inquiry(self)


        if data_dict.has_key('routingTable'):
            routing_table = data_dict['routingTable']
            for route in routing_table:
                self.routing_table[route.pop('ip')] = route
            if data_dict.has_key('more'):
                self.engage('NodeStore_dumpTable', page=page+1)
            else:
                print "======ROUTING TABLE======"
                for ip, route in self.routing_table.items():
                    print "%s - %s" % (self.show_nice_name(ip), route)
                print "======END ROUTING TABLE======"

        if self.function_name in('SwitchPinger_ping', 'RouterModule_pingNode'):
            print "======PING RESULT======"
            pprint.pprint(data_dict)

        if self.function_name == "ETHInterface_beginConnection":
            print "======Ethernet Connection======"
            pprint.pprint(data_dict)

        if self.function_name == "AdminLog_subscribe":
            pprint.pprint(data_dict, log_file)


    def close(self):
        self.finished = True
        self.client.report_completed_inquiry(self)


class CJDNSAdminClient(DatagramProtocol):

    timeout = 3

    actions = {
        'ping': {'q': 'ping'}
               }

    functions_available = {}
    messages = {}
    address_lookups = {}
    routing_table = {}
    known_names = {}

    open_inquiries = {}
    completed_inquiries = []

    queue = DeferredQueue()
    keepalive = False
    node_information = None


    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password
        self.countdown = self.timeout
        self.ponged = False

    def check_ponged(self):
        print "Checking if CJDNS admin has ponged: "
        if not self.ponged:
            print "No pong yet! We'll try pinging again soon."
            self.ping()
        else:
            print "Yep! CJDNS admin is responding."

    def ping(self):
        '''
        Pings the CJDNS Admin API for this node, ensuring it is up.
        If no pong is received within 1 second, try again.
        '''
        ping = bencoder.encode(self.actions['ping'])
        reactor.callLater(1, self.check_ponged)
        self.transport.write(ping, (self.host, self.port))

    def pong(self):
        if not self.ponged:
            self.ponged = True
            self.function_pages_registered = 0
            self.ask_for_functions(0)

    def engage(self, function_name, page=None, **kwargs):
        '''
        Begin an exchange with a CJDNS instance.
        Instantiates a CJDNSInquiry object and returns it.
        '''
        inquiry = CJDNSInquiry(self, function_name)
        txid = inquiry.request_cookie()
        self.open_inquiries[txid] = inquiry


###########################


        # If either page or kwargs['page'] is set, we'll pass that value.
#         if kwargs.get('page'):
#             call_args['page'] = kwargs.get('page')
#
#         if page is not None:
#             call_args['page'] = page
#
#         txid = self.get_cookie(txid)





#         self.function_queue[txid] = (function_name, call_args, page)



    def subscribe_to_log(self):
        self.engage("AdminLog_subscribe",
                    level=self.log_level
                    )
#         reactor.callLater(9, self.subscribe_to_log)  # TODO: This wasn't working.

    def ask_for_functions(self, page):
        availableFunctions = {}

        request_dict = {'q': 'Admin_availableFunctions', 'args': {'page': page}}
        self.transport.write(bencoder.encode(request_dict), (self.host, self.port))


    def register_functions(self, function_dict, more_to_come):
        self.functions_available.update(function_dict)
        self.function_pages_registered += 1

        if more_to_come:
            self.ask_for_functions(self.function_pages_registered)
        else:
            print "No more pages of functions.  Received %s" % self.function_pages_registered
            self.connection_complete()

    def connection_complete(self):
        pass

    def startProtocol(self):
        self.ping()
        if not self.keepalive:
            reactor.callLater(1, self.advance_countdown)

    def show_nice_name(self, ip):
        return self.known_names.get(ip) or ip

    def datagramReceived(self, data, (host, port)):
        '''
        A bunch of hastily cobbled logic around common function returs.
        TODO: Turn this into an actual messaging service.
        '''
        self.countdown = self.timeout
        data_dict = bencoder.decode(data)

        '''
        First, the two cases where we don't expect a txid: pong and availableFunctions.
        These don't involve a CJDNSInquiry - they affect this client object.
        '''

        if data_dict.get('q')  == "pong":
            return self.pong()

        if data_dict.has_key('availableFunctions'):
            functions_dict = data_dict['availableFunctions']
            return self.register_functions(functions_dict,
                                    more_to_come=True if ('more' in data_dict) else False)

        '''
        Second, we'll deal with logs.
        '''
        if data_dict.has_key('streamId'):
            return self.dispatch_log_event(data_dict)

        '''
        Now, the stuff for which we believe we already had an inquiry.
        '''
        txid = data_dict['txid']

        try:
            inquiry = self.open_inquiries.pop(txid)
        except Exception, e:
            raise

        if data_dict.has_key('cookie'): # We determine this to be a cookie
            new_txid = inquiry.consume_cookie(data_dict)
            self.open_inquiries[new_txid] = inquiry
            return new_txid

        else:
            return inquiry.receive_data(data_dict)





    def deal_with_result(result):
        pass


    def advance_countdown(self):
        self.countdown -= 1
        if self.countdown < 1:
            self.stop()
        else:
            print "Stopping in %s seconds unless there's more data." % self.countdown
            reactor.callLater(1, self.advance_countdown)

    def stop(self):
        print "No activity.  Stopping."
        self.stopProtocol()
        reactor.stop()

    def route_lookup(self, address):
        txid = random_string()
        self.address_lookups[txid] = address
        self.engage('RouterModule_lookup', txid, address=address)

    def get_node_information(self):
        return self.node_information

    def report_completed_inquiry(self, inquiry):
        self.completed_inquiries.append(inquiry)
        self.dispatch_result(inquiry)

    def dispatch_result(self, inquiry):
        pass

    def dispatch_log_event(self, data_dict):
        pass

