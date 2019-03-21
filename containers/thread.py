import json
from threading import Thread
from time import sleep

import requests

from containers.container_info import ContainerInfo
from containers.parser import parse_hash


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
        print('Collecting container info from cAdvisor')
        r = requests.get('http://localhost:8080/api/v2.0/spec/?type=docker&recursive=true')
        obj = json.loads(r.text)

        for key in obj.keys():
            h = parse_hash(str(key))
            if h not in self.containers:
                self.containers[h] = ContainerInfo(h, obj[key])

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
        :return: A dict without the keys for its own container and the DNS-container
        """
        filter_set = {'dadvisor', 'dns'}
        return {k: v for k, v in self.containers.items() if set(v.aliases) & filter_set == set()}

    def get_hash_from_ip(self, ip):
        """
        :param ip: the ip-address as a string
        :return: the full hash of the container ID
        """
        for info in self.containers.values():
            if info.ip == ip:
                return info.hash
        return ''
