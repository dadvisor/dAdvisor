import os
from threading import Thread
from time import sleep

import requests
from prometheus_client import Info

from ..datatypes.address import IP
from ..datatypes.peer import Peer
from ..log import log
from ..peers.peer_actions import fetch_peers, expose_peer


class PeersThread(Thread):

    def __init__(self):
        Thread.__init__(self, name='PeersThread')
        self.running = True
        self.sleep_time = 10
        self.my_peer = None
        self.peers = []
        self.init_peers()

    def set_my_peer(self, port):
        if os.environ.get('USE_TOR', default=False):
            self.my_peer = Peer(IP, str(80))
        else:
            self.my_peer = Peer(IP, port)
        self.my_peer.can_be_removed = False
        self.peers.append(self.my_peer)

    def run(self):
        while self.running:
            try:
                self.validate_peers()
            except Exception as e:
                log.error(e)
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
                log.info('Adding peer: {}, {}'.format(host, port))
                p = self.add_peer(host, port)
                p.can_be_removed = False

    def validate_peers(self):
        log.info('Validating peers: {}'.format(len(self.peers)))
        for p in self.other_peers:
            try:
                peer_list = fetch_peers(p)
                # Expose own node if it is not in the other_peers-list
                if self.my_peer not in peer_list:
                    expose_peer(self.my_peer, p)

                # Add new peers (if they're not in the list)
                for p2 in peer_list:
                    if p2 not in self.peers:
                        self.peers.append(p2)
            except requests.ConnectionError as e:
                log.error(e)
                if p.can_be_removed:
                    self.peers.remove(p)

    def get_peer_from_host(self, host):
        for peer in self.other_peers:
            if peer.host == host:
                return peer
        return None

    def add_peer(self, host, port):
        host_format = host.replace('.', '_')
        with open('/prometheus/{}.json'.format(host_format), 'w') as f:
            f.write("[{\"labels\": {\"job\": \"prometheus\"},\"targets\": [\"")
            f.write("{}:{}".format(host, port))
            f.write("\"]}]")

        info = Info('peer_{}'.format(host_format), 'Peer')
        info.info({'host': IP, 'port': port})

        p = Peer(host, port)
        if p not in self.peers:
            self.peers.append(p)
            expose_peer(self.my_peer, p)
        return p
