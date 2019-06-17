import json

from prometheus_client import Info

from dadvisor.config import IP, PROXY_PORT
from dadvisor.containers.cadvisor import get_machine_info
from dadvisor.datatypes.peer import Peer
from dadvisor.log import log
from dadvisor.peers.peer_actions import get_peer_list, register_peer, remove_peer, get_peer_info

FILENAME = '/prometheus-federation.json'
SLEEP_TIME = 60

PEER_INFO = Info('peer', 'Peers', ['host'])


class PeersCollector(object):
    """
    Collect information about other peers. The dAdvisor needs to be fully connected, as it needs to communicate with
    other peers if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self):
        self.running = True
        self.my_peer = None
        self.other_peers = []
        self.set_my_peer()

    def set_my_peer(self):
        self.my_peer = Peer(IP, PROXY_PORT)
        num_cores, memory = await get_machine_info()
        PEER_INFO.labels(host=IP).info({
            'port': str(PROXY_PORT),
            'num_cores': str(num_cores),
            'memory': str(memory)})

    @staticmethod
    async def set_peer_info(p, data):
        PEER_INFO.labels(host=p.host).info({
            'port': str(p.port),
            'num_cores': str(data['num_cores']),
            'memory': str(data['memory'])})

    async def run(self):
        """
        This run method performs the following two actions:
        1. register this peer in the tracker
        2. continuously perform the following actions:
            - validate other peers
        :return:
        """
        succeeded = False
        while not succeeded:
            try:
                await register_peer(self.my_peer)
                succeeded = True
            except Exception as e:
                log.error(e)

    @property
    def peers(self):
        return [self.my_peer] + self.other_peers

    def is_other_peer(self, host):
        return [p for p in self.other_peers if p.host == host]

    async def set_peers(self, peers):
        self.other_peers = []
        for p in peers:
            peer = Peer(p[0], p[1])
            if peer == self.my_peer:
                continue
            try:
                info = await get_peer_info(peer)
                await self.set_peer_info(peer, info)
                self.other_peers.append(peer)
            except Exception as e:
                log.error(e)
        self.set_scraper()

    def set_scraper(self):
        """ Set a line with federation information. Prometheus is configured in
        such a way that it reads this file. """
        try:
            with open(FILENAME, 'r') as file:
                old_data = file.read()
        except FileNotFoundError:
            old_data = ''

        peer_list = ['localhost:{}'.format(PROXY_PORT)]
        for p in self.other_peers:
            peer_list.append('{}:{}'.format(p.host, p.port))

        data = [{"labels": {"job": "promadvisor"}, "targets": peer_list}]
        new_data = json.dumps(data) + '\n'
        log.debug(new_data)

        if old_data != new_data:
            with open(FILENAME, 'w') as file:
                file.write(new_data)

    async def stop(self):
        self.running = False
        await remove_peer(self.my_peer)
