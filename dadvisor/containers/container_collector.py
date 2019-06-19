import asyncio
import json
import subprocess
from typing import Dict, List

from dadvisor.datatypes.container_info import ContainerInfo
from dadvisor.log import log

SLEEP_TIME = 30


class ContainerCollector(object):

    def __init__(self):
        self.running = True
        self.analyser_thread = None
        self.containers: List[ContainerInfo] = []

    async def run(self):
        """
        Performs the following two actions:
        - only at initialization: collect static information about the host price
        - continuously (every 30 sec) perform the following actions:
            - find new containers
            - validate own containers (find out ip address and if they're alive)
        :return:
        """

        while self.running:
            try:
                await asyncio.sleep(SLEEP_TIME)
                await self.collect_own_containers()
                await self.validate_own_containers()
            except Exception as e:
                log.error(e)
        log.info('ContainerCollector stopped')

    async def collect_own_containers(self):
        cmd = 'curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = json.loads(p.communicate()[0].decode('utf-8'))
        for c in data:
            if '/dadvisor' in c['Names']:
                continue
            if c['Id'] not in [c.hash for c in self.containers]:
                self.containers.append(ContainerInfo(c['Id'], c))

    async def validate_own_containers(self):
        for info in self.containers:
            info.validate()
            if info.stopped:
                self.containers.remove(info)
                continue

            for port_map in info.ports:
                if 'PublicPort' in port_map:
                    key = int(port_map['PublicPort'])
                    self.analyser_thread.port_mapping[key] = info.ip
                if 'PrivatePort' in port_map:
                    key = int(port_map['PrivatePort'])
                    self.analyser_thread.port_mapping[key] = info.ip

    @property
    def container_mapping(self) -> Dict[str, str]:
        """
        :return: A dict from local ip to container id
        """
        return {c.ip: c.hash for c in self.containers_filtered}

    def ip_to_hash(self, ip: str) -> str:
        if ip in self.container_mapping:
            return self.container_mapping[ip]

    @property
    def containers_filtered(self) -> List[ContainerInfo]:
        """
        :return: A dict without the key for its own container
        """
        skip = '/dadvisor'
        return [info for info in self.containers if skip not in info.names]

    def stop(self):
        self.running = False
        log.info('Stopping containerCollector')
