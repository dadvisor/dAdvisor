import asyncio
import json

from prometheus_client import Info

from dadvisor.config import INTERNAL_IP, PROXY_PORT
from dadvisor.datatypes.peer import Peer, from_list
from dadvisor.log import log
from dadvisor.peers.peer_actions import fetch_peers, expose_peer, get_peer_list, register_peer, get_tracker_info, ping, \
    remove_peer

FILENAME = '/prometheus-federation.json'
SLEEP_TIME = 60


class PeersCollector(object):
    """
    Collect information about other peers. The dAdvisor needs to be fully connected, as it needs to communicate with
    other peers if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self):
        self.running = True
        self.my_peer = Peer(INTERNAL_IP, PROXY_PORT)
        self.peers = [self.my_peer]
        self.parent = None
        self.children = []

    async def run(self):
        """
        This run method performs the following two actions:
        1. register this peer in the tracker
        2. continuously perform the following actions:
            - ask the tracker for its parent and children
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

        while self.running:
            try:
                await asyncio.sleep(SLEEP_TIME)
                await self.validate_node()
                await self.validate_peers()
            except Exception as e:
                log.error(e)

    @property
    def addresses(self):
        return [p.host for p in self.other_peers]

    @property
    def other_peers(self):
        return [p for p in self.peers if p != self.my_peer]

    def is_other_peer(self, host):
        return [p for p in self.other_peers if p.host == host]

    async def init_peers(self):
        """ Read peers from the tracker and add them to the list
        """
        for p in await get_peer_list():
            host, port = p
            if ping(host):
                await self.add_peer(host, port)

    async def validate_peers(self):
        log.info('Validating other peers: {}'.format(len(self.other_peers)))
        if not self.other_peers:
            await self.init_peers()

        for p in self.other_peers:
            try:
                if not ping(p.host):
                    raise Exception('peer not up')
            except Exception as e:
                log.error(e)
                if p in self.peers:
                    self.peers.remove(p)
                    await remove_peer(p)
                continue

            try:
                peer_list = await fetch_peers(p)
                # Expose own node if it is not in the other_peers-list
                if self.my_peer not in peer_list:
                    await expose_peer(self.my_peer, p)

                # Add new peers (if they're not in the list)
                for p2 in peer_list:
                    if p2 not in self.peers:
                        await self.add_peer(p2.host, p2.port)
            except Exception as e:
                log.error(e)
                if p in self.peers:
                    self.peers.remove(p)

    def get_peer_from_host(self, host):
        for peer in self.other_peers:
            if peer.host == host:
                return peer
        return None

    async def add_peer(self, host, port):
        host_format = host.replace('.', '_')
        log.error('host: {}, port: {}'.format(host, port))

        try:
            info = Info('peer_{}'.format(host_format), 'Peer')
            info.info({
                'host': host,
                'port': str(port)
            })
        except ValueError:
            pass

        p = Peer(host, port)
        try:
            if p not in self.peers:
                self.peers.append(p)
                log.error('Adding peer: {}'.format(p))
                await expose_peer(self.my_peer, p)
        except Exception as e:
            log.error(e)
        return p

    async def validate_node(self):
        """
        Ask the tracker for its children and it's parent.
        For the children, let it scrape by prometheus
        :return:
        """
        data = await get_tracker_info(self.my_peer)
        self.parent = None
        if 'parent' in data and data['parent']:
            self.parent = from_list(data['parent'])
        self.children = []
        if 'children' in data and data['children']:
            for child in data['children']:
                self.children.append(from_list(child))
        self.set_scraper()

    def set_scraper(self):
        """ Set a line with federation information. Prometheus is configured in
        such a way that it reads this file. """
        try:
            with open(FILENAME, 'r') as file:
                old_data = file.read()
        except FileNotFoundError:
            old_data = ''

        child_list = []
        for child in self.children:
            child_list.append('{}:{}'.format(child.host, child.port))

        data = [{"labels": {"job": "promadvisor"}, "targets": child_list}]
        new_data = json.dumps(data) + '\n'
        log.debug(new_data)

        if old_data != new_data:
            with open(FILENAME, 'w') as file:
                file.write(new_data)
