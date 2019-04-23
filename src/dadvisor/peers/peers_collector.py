import asyncio
import json

from prometheus_client import Info

from dadvisor.config import INTERNAL_IP, IP, PROXY_PORT
from dadvisor.datatypes.peer import Peer, from_list
from dadvisor.log import log
from dadvisor.peers.peer_actions import fetch_peers, expose_peer, get_ip, get_peer_list, register_peer, get_tracker_info

SLEEP_TIME = 10
FILENAME = '/prometheus-federation.json'


class PeersCollector(object):

    def __init__(self):
        self.running = True
        self.my_peer = None
        self.peers = []  # List of Peer
        self.host_mapping = {INTERNAL_IP: IP}  # a dict from internal IP to external IP
        self.set_my_peer()

        self.parent = None
        self.children = []

    def set_my_peer(self):
        self.my_peer = Peer(IP, PROXY_PORT)
        self.peers.append(self.my_peer)

    async def run(self):
        await register_peer(self.my_peer)
        while self.running:
            await asyncio.sleep(SLEEP_TIME)
            await self.validate_peers()
            await self.validate_node()

    @property
    def other_peers(self):
        return [p for p in self.peers if p != self.my_peer]

    def is_other_peer(self, host):
        return [p for p in self.other_peers if p.host == host]

    async def init_peers(self):
        """ Read peers from an external address and add them to the list
        """
        for p in await get_peer_list():
            host, port = p
            internal, external = await get_ip(p)
            self.host_mapping[internal] = external
            await self.add_peer(host, port)

    async def validate_peers(self):
        log.info('Validating other peers: {}'.format(len(self.other_peers)))
        if not self.other_peers:
            await self.init_peers()
        for p in self.other_peers:
            # Create mapping
            try:
                internal, external = await get_ip(p)
                self.host_mapping[internal] = external
            except Exception:
                log.error('Cannot connect to peer: {}'.format(p))
                if p in self.peers:
                    self.peers.remove(p)

            try:
                peer_list = await fetch_peers(p)
                # Expose own node if it is not in the other_peers-list
                if self.my_peer not in peer_list:
                    await expose_peer(self.my_peer, p)

                # Add new peers (if they're not in the list)
                for p2 in peer_list:
                    if p2 not in self.peers:
                        await self.add_peer(p2.host, p2.address)
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

        try:
            info = Info('peer_{}'.format(host_format), 'Peer')
            info.info({'host': IP, 'port': str(port)})
        except ValueError:
            pass

        p = Peer(host, port)
        try:
            if p not in self.peers:
                self.peers.append(p)
                log.info('Adding peer: {}'.format(p))
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
        if data['parent']:
            self.parent = from_list(data['parent'])
        self.children = []
        for child in data['children']:
            self.children.append(from_list(child))
        self.set_scraper()

    def set_scraper(self):
        """ Set a line with federation information """
        try:
            with open(FILENAME, 'r') as file:
                old_data = file.read()
        except FileNotFoundError:
            old_data = ''

        child_list = []
        for child in self.children:
            child_list.append("{}:{}".format(child.host, child.port))
        child_list = [', '.join(child_list)] if ', '.join(child_list) else []

        data = [{"labels": {"job": "promadvisor"}, "targets": child_list}]
        new_data = json.dumps(data) + '\n'

        if old_data != new_data:
            with open(FILENAME, 'w') as file:
                file.write(new_data)
