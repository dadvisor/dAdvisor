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
        self.old_containers = []  # list of ContainerInfo objects
        self.other_containers = []  # list of ContainerMapping objects
        self.analyser_thread = None

    async def run(self):
        while self.running:
            await asyncio.sleep(SLEEP_TIME)
            await self.collect_own_containers()
            await self.collect_remote_containers()
            await self.validate_own_containers()

    async def collect_own_containers(self):
        cmd = 'curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = json.loads(p.communicate()[0].decode('utf-8'))
        for c in data:
            if c['Image'].endswith('dadvisor'):
                continue
            if c['Id'] not in [c.hash for c in self.own_containers]:
                self.own_containers.append(ContainerInfo(c['Id'], c))

    async def validate_own_containers(self):
        for info in self.own_containers:
            info.validate()
            if info.stopped:
                self.own_containers.remove(info)
                self.old_containers.append(info)
                continue

            for port_map in info.ports:
                if 'PublicPort' in port_map:
                    key = str(port_map['PublicPort'])
                    if key not in self.analyser_thread.port_mapping and info.ip:
                        self.analyser_thread.port_mapping[key] = info.ip

    def get_all_containers(self):
        return self.other_containers + \
               [c.to_container_mapping(IP) for c in self.containers_filtered]

    async def collect_remote_containers(self):
        for p in self.peers_collector.other_peers:
            containers = get_containers(p)
            # remove previous containers
            for c in self.other_containers:
                if c.host == p.host:
                    self.other_containers.remove(c)
            for c in containers:
                if c['ip']:  # only add containers that have an ip
                    self.other_containers.append(ContainerMapping(p.host, c['ip'], c['image'], c['hash']))

    @property
    def containers_filtered(self):
        """
        :return: A dict without the key for its own container
        """
        skip = '/dadvisor'
        return [info for info in self.own_containers if skip not in info.names]
