import asyncio
from threading import Thread

from asyncio import Queue
from prometheus_client import Counter

from dadvisor.config import IP
from dadvisor.datatypes.address import Address
from dadvisor.log import log
from dadvisor.peers.peer_actions import get_ports


class AnalyserThread(Thread):

    def __init__(self, inspector_thread, container_collector, peers_collector):
        Thread.__init__(self, name='AnalyserThread')
        container_collector.analyser_thread = self
        self.running = True
        self.inspector_thread = inspector_thread
        self.container_collector = container_collector
        self.peers_collector = peers_collector
        self.port_mapping = {}  # a dict from port to container_id
        self.counter = Counter('bytes_send', 'Number of bytes send between two nodes', ['src', 'dst'])
        self.loop = asyncio.new_event_loop()

    def run(self):
        self.loop.create_task(self.async_run())
        self.loop.run_forever()

    async def async_run(self):
        self.inspector_thread.data = Queue()

        while self.running:
            dataflow = await self.inspector_thread.data.get()
            log.info(dataflow)
            self.add_port(dataflow.src)
            self.add_port(dataflow.dst)
            self.resolve_local_address(dataflow.src)
            self.resolve_local_address(dataflow.dst)

            await self.resolve_remote_address(dataflow.dst)

            src_id = self.address_id(dataflow.src)
            dst_id = self.address_id(dataflow.dst)
            log.info(dataflow)

            if not src_id or not dst_id:
                self.inspector_thread.data.task_done()
                continue

            self.counter.labels(src=id_map(src_id), dst=id_map(dst_id)).inc(dataflow.size)
            self.inspector_thread.data.task_done()

    def add_port(self, address):
        if address.is_local():
            self.port_mapping[address.port] = address.container

    def resolve_port(self, port):
        if port in self.port_mapping:
            return Address(IP, self.port_mapping[port], port)
        return None

    def resolve_local_address(self, address):
        if address.host in self.peers_collector.host_mapping:
            address.host = self.peers_collector.host_mapping[address.host]

        if address.host == IP:
            for info in self.container_collector.own_containers:
                for port_map in info.ports:
                    if 'PublicPort' in port_map and str(port_map['PublicPort']) == str(address.port):
                        address.container = info.ip
                        if 'PrivatePort' in port_map:
                            address.port = str(port_map['PrivatePort'])
                        return

    async def resolve_remote_address(self, address):
        if address.host != IP:
            p = self.peers_collector.get_peer_from_host(address.host)
            if p:
                ports = await get_ports(p)
                if address.port in ports:
                    address.container = ports[address.port]

    # def get_edges(self):
    #     """
    #     :return: A list with a dict per data-flow of the containers
    #     """
    #     edges = []
    #     for src_id in self.container_thread.get_all_containers():
    #         for dst_id in [dst_id for dst_id in self.container_thread.get_all_containers() if
    #                        dst_id != src_id and
    #                        self.counter.labels(id_map(src_id), id_map(dst_id))._value.get() > 0]:
    #             edges.append({'data': {
    #                 'source': id_map(src_id),
    #                 'target': id_map(dst_id),
    #                 'bytes': self.counter.labels(id_map(src_id), id_map(dst_id))._value.get()
    #             }})
    #     return edges

    def address_id(self, address):
        """
        Get the local address from a given host (assuming that this host is a peer)
        :param address:
        :return:
        """
        for item in list(self.container_collector.get_all_containers()):
            if address.host == item.host and address.container == item.container_ip:
                return item
        return ''


def id_map(container):
    try:
        c_id = container.id
    except AttributeError:
        try:
            c_id = container['id']
        except TypeError:
            c_id = container
    return 'id_{}'.format(c_id)
