import asyncio
import json
import subprocess

from dadvisor.config import IP
from dadvisor.datatypes.container_info import ContainerInfo
from dadvisor.datatypes.container_mapping import ContainerMapping
from dadvisor.peers.peer_actions import get_containers

SLEEP_TIME = 5


class ContainerCollector(object):

    def __init__(self, peers_collector):
        self.peers_collector = peers_collector
        self.running = True
        self.own_containers = []  # list of ContainerInfo objects
        self.remote_containers = []  # list of ContainerMapping objects
        self.analyser_thread = None

    async def run(self):
        while self.running:
            await asyncio.sleep(SLEEP_TIME)
            await self.collect_own_containers()
            await self.validate_own_containers()
            await self.collect_remote_containers()

    async def collect_own_containers(self):
        cmd = 'curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = json.loads(p.communicate()[0].decode('utf-8'))
        for c in data:
            if c['Image'].endswith('dadvisor'):
                continue
            if c['Id'] not in [c.hash for c in self.own_containers]:
                self.own_containers.append(ContainerInfo(c['Id'], c))

    async def collect_remote_containers(self):
        """ Ask every peer for a list of containers. """
        for peer in self.peers_collector.other_peers:
            container_list = await get_containers(peer)
            self.remote_containers = [c for c in self.remote_containers if c.host != peer.host]
            for c in container_list:
                self.remote_containers.append(ContainerMapping(c['host'], c['container'],
                                                               c['image'], c['id']))

    async def validate_own_containers(self):
        for info in self.own_containers:
            info.validate()
            if info.stopped:
                self.own_containers.remove(info)
                continue

            for port_map in info.ports:
                if 'PublicPort' in port_map:
                    key = str(port_map['PublicPort'])
                    if key not in self.analyser_thread.port_mapping and info.ip:
                        self.analyser_thread.port_mapping[key] = info.ip

    def get_own_containers(self):
        return [c.to_container_mapping(IP) for c in self.containers_filtered]

    def get_all_containers(self):
        return self.get_own_containers() + self.remote_containers

    @property
    def containers_filtered(self):
        """
        :return: A dict without the key for its own container
        """
        skip = '/dadvisor'
        return [info for info in self.own_containers if skip not in info.names]
