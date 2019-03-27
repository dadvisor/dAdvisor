import json
import subprocess
from threading import Thread
from time import sleep

from containers.container_info import ContainerInfo


class ContainerThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.sleep_time = 10
        self.containers = {}

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
        data = {str(k): str(v) for k, v in data.items()}

        for c in data:
            print(c)
            if c.Id not in self.containers:
                self.containers[c.Id] = ContainerInfo(c.Id, c)

    def get_nodes(self, ip, hash_length):
        """
        :return: A list of dicts with the containers
        """
        nodes = self.containers_filtered()
        images = set(v.image for v in nodes.values())
        return [{'data': {'id': ip,
                          'name': ip}}] + \
               [{'data': {'id': ip + i,
                          'parent': ip,
                          'name': i}} for i in images] + \
               [{'data': {'id': k[:hash_length],
                          'parent': ip + v.image,
                          'name': k[:hash_length]}} for k, v in nodes.items()]

    def containers_filtered(self):
        """
        :return: A dict without the key for its own container
        """
        skip = 'dadvisor'
        return {k: v for k, v in self.containers.items() if skip in v.aliases}

    def get_hash_from_ip(self, ip):
        """
        :param ip: the ip-address as a string
        :return: the full hash of the container ID
        """
        for info in self.containers.values():
            if info.ip == ip:
                return info.hash
        return ''
