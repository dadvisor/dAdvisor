import json
import subprocess
from threading import Thread
from time import sleep

from datatypes.address import IP
from datatypes.container_mapping import ContainerMapping
from datatypes.container_info import ContainerInfo
from datatypes.database import Database


class ContainerThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.sleep_time = 10
        self.own_containers = Database()  # database of ContainerInfo objects
        self.all_containers = Database()  # database of ContainerMapping objects

    def run(self):
        while self.running:
            try:
                self.collect_container_info()
            except Exception as e:
                print(e)
            sleep(self.sleep_time)

    def collect_container_info(self):
        cmd = 'curl --unix-socket /var/run/docker.sock http://localhost/containers/json'
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        data = json.loads(p.communicate()[0].decode('utf-8'))
        for c in data:
            if c['Id'] not in [c.hash for c in self.own_containers]:
                container_info = ContainerInfo(c['Id'], c)
                self.own_containers.add(container_info)
                self.all_containers.add(ContainerMapping.decode(c, container_info))

    def get_nodes(self, hash_length):
        """
        :return: A list of dicts with the containers
        """
        nodes = self.containers_filtered
        images = set([v.image for v in nodes])
        return [{'data': {'id': IP,
                          'name': IP}}] + \
               [{'data': {'id': IP + i,
                          'parent': IP,
                          'name': i}} for i in images] + \
               [{'data': {'id': node.hash[:hash_length],
                          'parent': IP + node.image,
                          'name': node.hash[:hash_length]}} for node in nodes]

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
        return [info for info in self.own_containers if skip not in info.names]

    def get_hash_from_ip(self, ip):
        """
        :param ip: the ip-address as a string
        :return: the full hash of the container ID
        """
        for info in self.own_containers:
            if info.ip == ip:
                return info.hash
        return ''
