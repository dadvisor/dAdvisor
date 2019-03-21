from threading import Thread
from time import sleep

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

    def add_peer(self, host, port):
        p = Peer(host, port)
        self.peers.append(p)
        return p
