import os
from threading import Thread
from time import sleep

import requests

from datatypes.database import Database
from datatypes.peer import Peer
from datatypes.address import IP, Address


class PeersThread(Thread):

    def __init__(self, port):
        Thread.__init__(self)
        self.running = True
        self.sleep_time = 10
        self.my_peer = Peer(IP, port)
        self.my_peer.can_be_removed = False
        self.peers = Database(self.my_peer)

        self.init_peers()

    def run(self):
        while self.running:
            try:
                self.validate_peers()
            except Exception as e:
                print(e)
            sleep(self.sleep_time)

    @property
    def other_peers(self):
        return [p for p in self.peers if p != self.my_peer]

    def is_other_peer(self, host):
        return [p for p in self.other_peers if p.host == host]

    def init_peers(self):
        """ Read peers from the environment variable and add them to the list.
            input: OTHER_PEERS=35.204.153.106:8800,35.204.153.106:8800
        """
        peers = os.environ.get('OTHER_PEERS', '')
        if peers != '':
            for peer in peers.split(','):
                host, port = peer.split(':')
                p = self.add_peer(host, port)
                p.can_be_removed = False

    def validate_peers(self):
        print('Validating peers: {}'.format(len(self.peers)))
        for p in self.other_peers:
            try:
                peer_list = requests.get('http://{}:{}/peers'.format(p.host, p.port)).json()
                peer_list = [Peer(p2['host'], p2['port']) for p2 in peer_list]
                # Expose own node if it is not in the other_peers-list
                if self.my_peer not in peer_list:
                    self.request_other_peer(p)

                # Add new peers (if they're not in the list)
                for p2 in peer_list:
                    if p2 not in self.peers:
                        self.peers.add(p2)
            except requests.ConnectionError as e:
                print('Connection error: {}'.format(e))
                if p.can_be_removed:
                    self.peers.remove(p)

    def request_other_peer(self, p):
        try:
            requests.get(
                'http://{}:{}/peers/add/{}:{}'.format(p.host, p.port,
                                                      self.my_peer.host, self.my_peer.port)).json()
        except Exception:
            print('Cannot send an address to {}'.format(p))

    def resolve_address(self, address):
        p = self.get_peer_from_host(address.host)
        try:
            data = requests.get('http://{}:{}/container/{}'.format(p.host, p.port, address.port)).json()
            return Address(data['host'], data['container'], data['port'])
        except Exception:
            print('Cannot validate data from {}'.format(p))
            raise

    def get_peer_from_host(self, host):
        for peer in self.other_peers:
            if peer.host == host:
                return peer
        return None

    def add_peer(self, host, port):
        p = Peer(host, port)
        if p not in self.peers:
            self.peers.add(p)
            self.request_other_peer(p)
        return p
