from threading import Thread
from time import sleep

import requests

from peers.peer import Peer
from web import IP
import os


class PeersThread(Thread):

    def __init__(self, port):
        Thread.__init__(self)
        self.running = True
        self.sleep_time = 10
        self.my_peer = Peer(IP, port)
        self.peers = [self.my_peer]

        self.init_peers()

    def run(self):
        while self.running:
            try:
                self.validate_peers()
            except Exception as e:
                print(e)
            sleep(self.sleep_time)

    def init_peers(self):
        """ Read peers from the environment variable and add them to the list.
            input: OTHER_PEERS=35.204.153.106:8800,35.204.153.106:8800
        """
        peers = os.environ.get('OTHER_PEERS', '')
        if peers != '':
            for peer in peers.split(','):
                host, port = peer.split(':')
                self.add_peer(host, port)

    def validate_peers(self):
        print('Validating peers: {}'.format(len(self.peers)))
        for p in self.peers:
            if p == self.my_peer:  # don't validate its own peer
                continue
            try:
                other_peers = requests.get('http://{}:{}/peers'.format(p.host, p.port)).json()
                other_peers = [Peer(p2['host'], p2['port']) for p2 in other_peers]
                # Expose own node if it is not in the other_peers-list
                if self.my_peer not in other_peers:
                    requests.get(
                        'http://{}:{}/peers/add/{}:{}'.format(p.host, p.port, self.my_peer.host,
                                                              self.my_peer.port)).json()

                # Add new peers (if they're not in the list)
                for p2 in other_peers:
                    if p2 not in self.peers:
                        self.peers.append(p2)
            except requests.ConnectionError as e:
                print('Connection error: {}'.format(e))
                self.peers.remove(p)

    def add_peer(self, host, port):
        p = Peer(host, port)
        self.peers.append(p)
        return p
