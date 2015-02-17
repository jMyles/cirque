Cirque is an admin for mesh networking nodes. It currently only supports CJDNS. It uses Django for the interface, and Hendrix to communicate with the nodes.

Cirque is still very much in development. At this point you should only install this if you are developing it.

# Installing

    pip install -r requirements.txt

# Running

    cd cirque
    python cirque_django.py

Unless you're connected to a CJDNS network, you'll now see command line output it saying that it can't connect.

Point your browser to http://localhost:8010/ to look at the interface.
