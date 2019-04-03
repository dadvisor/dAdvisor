from threading import Thread

import requests

from datatypes.address import IP, Address
from log import log

MAX_WIDTH = 10.0


class AnalyserThread(Thread):

    def __init__(self, inspector_thread, container_thread, peers_thread):
        Thread.__init__(self)
        self.running = True
        self.inspector_thread = inspector_thread
        self.container_thread = container_thread
        self.peers_thread = peers_thread
        self.data = {}  # 2D dict, that can be used as: self.data[src][dst] = data size
        self.ports = {}  # a dict from port to container_id

    def run(self):
        while self.running:
            dataflow = self.inspector_thread.data.get()
            self.add_port(dataflow.src)
            self.add_port(dataflow.dst)
            self.resolve_local_address(dataflow.src)
            self.resolve_local_address(dataflow.dst)

            self.resolve_remote_address(dataflow.src)
            src_id = self.address_id(dataflow.src)
            dst_id = self.address_id(dataflow.dst)

            if src_id == -1 or dst_id == -1:
                continue
            log.info(dataflow)

            if src_id in self.data:
                if dst_id in self.data[src_id]:
                    self.data[src_id][dst_id] += dataflow.size
                else:
                    self.data[src_id][dst_id] = dataflow.size
            else:
                self.data[src_id] = {}
                self.data[src_id][dst_id] = dataflow.size

    def add_port(self, address):
        if address.is_local():
            self.ports[address.port] = address.container

    def resolve_port(self, port):
        if port in self.ports:
            return Address(IP, self.ports[port], port)
        return None

    def resolve_local_address(self, address):
        if address.host != IP:
            return
        for info in self.container_thread.own_containers:
            for port_map in info.ports:
                if str(port_map['PublicPort']) == str(address.port):
                    address.container = info.ip
                    address.port = str(port_map['PrivatePort'])
                    return

    def resolve_remote_address(self, address):
        if address.host != IP:
            p = self.peers_thread.get_peer_from_host(address.host)
            if p:
                try:
                    ports = requests.get('http://{}:{}/ports'.format(p.host, p.port)).json()
                    if address.port in ports:
                        address.container = ports[address.port]
                except Exception:
                    log.warn('Cannot retrieve ports from peer')
                    raise

    def get_edges(self):
        """
        :return: A list with a dict per data-flow of the containers
        """
        edges = []
        containers = self.container_thread.get_all_containers()
        for src_id in self.data:
            for dst_id in self.data[src_id]:
                edges.append({'data': {
                    'source': containers[src_id].id,
                    'target': containers[dst_id].id,
                    'bytes': self.data[src_id][dst_id]
                }})
        return self.adjust_width(edges)

    def address_id(self, address):
        """
        Get the local address from a given host (assuming that this host is a peer)
        :param address:
        :return:
        """
        for index, item in enumerate(self.container_thread.get_all_containers()):
            if address.host == item.host and address.container == item.container_ip:
                return index
        return -1

    @staticmethod
    def adjust_width(edges):
        try:
            max_width = max([edge['data']['bytes'] for edge in edges])
            scale = MAX_WIDTH / max_width
        except ValueError:
            scale = 1
        for edge in edges:
            edge['data']['width'] = edge['data']['bytes'] * scale
        return edges
