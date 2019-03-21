from threading import Thread
from time import sleep

import requests

from peers.peer import Peer


class PeersThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.sleep_time = 10
        self.peers = []

    def run(self):
        while self.running:
            try:
                self.validate_peers()
            except Exception as e:
                print(e)
            sleep(self.sleep_time)

    def validate_peers(self):
        # TODO: implement method
        print('Validating peers')
        for p in self.peers:
            try:
                json = requests.get('http://{}:{}/peers'.format(p.host, p.port)).json()
                print(json)
            except requests.ConnectionError as e:
                print('Connection error: {}'.format(e))
                self.peers.remove(p)

    def add_peer(self, host, port):
        p = Peer(host, port)
        self.peers.append(p)
        return p
