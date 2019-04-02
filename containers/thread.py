import json
import subprocess
from threading import Thread
from time import sleep

import requests

from datatypes.address import IP
from datatypes.container_info import ContainerInfo
from datatypes.container_mapping import ContainerMapping
from log import log


class ContainerThread(Thread):

    def __init__(self, peers_thread):
        Thread.__init__(self)
        self.peers_thread = peers_thread
        self.running = True
        self.sleep_time = 10
        self.own_containers = []  # list of ContainerInfo objects
        self.other_containers = []  # list of ContainerMapping objects
        self.analyser_thread = None

    def run(self):
        while self.running:
            try:
                self.collect_own_containers()
                self.collect_remote_containers()
                self.validate_own_containers()
            except Exception as e:
                log.error(e)
            sleep(self.sleep_time)

    def collect_own_containers(self):
        cmd = 'curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = json.loads(p.communicate()[0].decode('utf-8'))
        for c in data:
            if c['Id'] not in [c.hash for c in self.own_containers]:
                info = ContainerInfo(c['Id'], c)
                for port_map in info.ports:
                    self.analyser_thread.ports[str(port_map['PublicPort'])] = info.ip
                self.own_containers.append(info)

    def validate_own_containers(self):
        for info in self.own_containers:
            info.validate()

    def get_all_containers(self):
        return self.other_containers + \
               [c.to_container_mapping(IP) for c in self.containers_filtered]

    def collect_remote_containers(self):
        for p in self.peers_thread.other_peers:
            containers = requests.get('http://{}:{}/containers'.format(p.host, p.port)).json()
            id_set = set([c.id for c in self.other_containers])
            for c in containers:
                if c['hash'] not in id_set and c['ip']:  # only add containers that have an ip
                    self.other_containers.append(ContainerMapping(p.host, c['ip'], c['image'], c['hash']))

    def get_nodes(self, hash_length):
        """
        :return: A list of dicts with the containers
        """
        all_containers = self.get_all_containers()
        hosts = set([c.host for c in all_containers])
        images = {}
        for container in all_containers:
            if container.host not in images:
                images[container.host] = {container.image}
            else:
                images[container.host].add(container.image)

        data = [{'data': {'id': host,
                          'name': host}} for host in hosts]
        for host, image_set in images.items():
            data += [{'data': {'id': host + i,
                               'parent': host,
                               'name': i}} for i in image_set]
        data += [{'data': {'id': c.id,
                           'parent': c.host + c.image,
                           'name': c.id[:hash_length]}} for c in all_containers]
        return data

    def to_internal_port(self, port):
        """
        Converts a public port to a private port. Returns the given port if no mapping is found
        :param port: the port to map
        :return:
        """
        for container in self.containers_filtered:
            for port_mapping in container.ports:
                if port_mapping['PublicPort'] == int(port):
                    return int(port_mapping['PrivatePort'])
        return port

    @property
    def containers_filtered(self):
        """
        :return: A dict without the key for its own container
        """
        skip = '/dadvisor'
        return [info for info in self.own_containers if skip not in info.names and not info.stopped]
