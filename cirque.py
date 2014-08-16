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

import sys
import os
import socket
import hashlib
import json
import threading
import time
import Queue
import random
import string
import bencoder
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.defer import DeferredQueue, QueueUnderflow
from twisted.internet import reactor
import publicToIp6

BUFFER_SIZE = 69632
KEEPALIVE_INTERVAL_SECONDS = 2


class Session():
    """Current cjdns admin session"""

    def __init__(self, socket):
        self.socket = socket
        self.queue = Queue.Queue()
        self.messages = {}

    def disconnect(self):
        self.socket.close()

    def getMessage(self, txid):
        # print self, txid
        return _getMessage(self, txid)

    def functions(self):
        print(self._functions)





def _randomString():
    """Random string for message signing"""

    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(10))




class TwistedSession(DatagramProtocol):

    actions = {
        'ping': {'q': 'ping'}
               }

    ponged = False

    functions = {}
    function_queue = {}
    messages = {}
    address_lookups = {}

    queue = DeferredQueue()


    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

    def check_ponged(self):
        if not self.ponged:
            print "No pong yet! We'll try pinging again."
            self.ping()
        else:
            print "Received a pong."

    def ping(self):
        print "Pinging."
        ping = bencoder.encode(self.actions['ping'])
        reactor.callLater(1, self.check_ponged)
        self.transport.write(ping, (self.host, self.port))

    def pong(self):
        if not self.ponged:
            self.ponged = True
            self.function_pages_registered = 0
            self.ask_for_functions(0)

    def get_cookie(self, txid=None):
        if not txid:
            txid = _randomString()

        # print "requesting cookie for %s" % txid

        request = {'q': 'cookie', 'txid': txid}
        self.transport.write(bencoder.encode(request), (self.host, self.port))
        return txid

    def engage(self, function_name, txid=None, **kwargs):
        call_args = {}

        default_args = self.functions[function_name]

        for arg in default_args:
            if arg not in kwargs:
                # If the user didn't specify a value (ie, they didn't override the value for this kwarg)
                # then we'll assume they want the default.
                call_args[arg] = default_args[arg]
            else:
                # ...otherwise, we go with their kwarg.
                call_args[arg] = kwargs[arg]


        txid = self.get_cookie(txid)
        self.function_queue[txid] = (function_name, call_args)

    def call_function(self, cookie, function_name, call_args, txid=None, password=None):
        if not password:
            password=self.password

        if not txid:
            txid = _randomString()

        pass_hash = hashlib.sha256(password + cookie).hexdigest()

        req = {
            'q': 'auth',
            'aq': function_name,
            'hash': pass_hash,
            'cookie': cookie,
            'args': call_args,
            'txid': txid
        }
        first_time_benc_req = bencoder.encode(req)
        req['hash'] = hashlib.sha256(first_time_benc_req).hexdigest()
        second_time_benc_req = bencoder.encode(req)
        print "Calling function: %s" % req
        self.transport.write(second_time_benc_req, (self.host, self.port))



    def ask_for_functions(self, page):
        availableFunctions = {}

        request_dict = {'q': 'Admin_availableFunctions', 'args': {'page': page}}
        self.transport.write(bencoder.encode(request_dict), (self.host, self.port))


    def register_functions(self, function_dict, more_to_come):
        self.functions.update(function_dict)
        self.function_pages_registered += 1

        if more_to_come:
            self.ask_for_functions(self.function_pages_registered)
        else:
            print "No more pages of functions.  Received %s" % self.function_pages_registered
            self.connection_complete()

    def connection_complete(self):
        pass

    def startProtocol(self):
#         self.transport.connect(self.host, self.port)
        self.ping()



    def datagramReceived(self, data, (host, port)):
        data_dict = bencoder.decode(data)
        # print "Received data! It's %s" % data_dict
        self.queue.put(data_dict)

        if data_dict.get('q')  == "pong":
            self.pong()

        if data_dict.has_key('availableFunctions'):
            functions_dict = data_dict['availableFunctions']
            self.register_functions(functions_dict,
                                    more_to_come=True if ('more' in data_dict) else False)

        if data_dict.has_key('cookie'): # We determine this to be a cookie
            function_name, call_args = self.function_queue[data_dict['txid']]
            return self.call_function(data_dict['cookie'], function_name, call_args, txid=data_dict['txid'])

        if data_dict.has_key('peers'):
            for peer in data_dict['peers']:
                peer_address =  publicToIp6.PublicToIp6_convert(peer['publicKey'])
                print "key: %s addy: %s" % (peer['publicKey'], peer_address)
                self.route_lookup(peer_address)

        if data_dict.get('txid'):
            if data_dict['txid'] in self.address_lookups.keys():
                print "%s has a route: %s" % (self.address_lookups[data_dict['txid']], data_dict['result'])

    def route_lookup(self, address):
        txid = _randomString()
        self.address_lookups[txid] = address
        self.engage('RouterModule_lookup', txid, address=address)





def connect(ipAddr, port, password):
    """Connect to cjdns admin with this attributes"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ipAddr, port))
    sock.settimeout(2)

    # Make sure it pongs.
    sock.send('d1:q4:pinge')
    data = sock.recv(BUFFER_SIZE)
    if (data != 'd1:q4:ponge'):
        raise Exception(
            "Looks like " + ipAddr + ":" + str(port) +
            " is to a non-cjdns socket.")

    # Get the functions and make the object
    page = 0
    availableFunctions = {}
    while True:
        sock.send(
            'd1:q24:Admin_availableFunctions4:argsd4:pagei' +
            str(page) + 'eee')
        data = sock.recv(BUFFER_SIZE)
        benc = bdecode(data)
        for func in benc['availableFunctions']:
            availableFunctions[func] = benc['availableFunctions'][func]
        if (not 'more' in benc):
            break
        page = page+1

    funcArgs = {}
    funcOargs = {}

    for (i, func) in availableFunctions.items():
        items = func.items()

        # grab all the required args first
        # append all the optional args
        rargList = [arg for arg,atts in items if atts['required']]
        argList = rargList + [arg for arg,atts in items if not atts['required']]

        # for each optional arg setup a default value with
        # a type which will be ignored by the core.
        oargList = {}
        for (arg,atts) in items:
            if not atts['required']:
                oargList[arg] = (
                    "''" if (func[arg]['type'] == 'Int')
                    else "0")



        setattr(Session, i, _functionFabric(
            i, argList, oargList, password))

        funcArgs[i] = rargList
        funcOargs[i] = oargList

    session = Session(sock)

    kat = threading.Thread(target=_receiverThread, args=[session])
    kat.setDaemon(True)
    kat.start()

    # Check our password.
    ret = _callFunc(session, "ping", password, {})
    if ('error' in ret):
        raise Exception(
            "Connect failed, incorrect admin password?\n" + str(ret))

    session._functions = ""

    funcOargs_c = {}
    for func in funcOargs:
        funcOargs_c[func] = list(
            [key + "=" + str(value)
                for (key, value) in funcOargs[func].items()])

    for func in availableFunctions:
        session._functions += (
            func + "(" + ', '.join(funcArgs[func] + funcOargs_c[func]) + ")\n")

    # print session.functions
    return session


def connectWithAdminInfo(path = None):
    """Connect to cjdns admin with data from user file"""

    if path is None:
        path = os.path.expanduser('~/.cjdnsadmin')
    try:
        with open(path, 'r') as adminInfo:
            data = json.load(adminInfo)
    except IOError:
        print('Please create a file named .cjdnsadmin in your ')
        print('home directory with')
        print('ip, port, and password of your cjdns engine in json.')
        print('for example:')
        print('{')
        print('    "addr": "127.0.0.1",')
        print('    "port": 11234,')
        print('    "password": "You tell me! (Search in ~/cjdroute.conf)"')
        print('}')
        raise

    return connect(data['addr'], data['port'], data['password'])
