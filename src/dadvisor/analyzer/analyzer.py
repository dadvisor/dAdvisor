from collections import OrderedDict
from typing import Dict

from prometheus_client import Counter

from dadvisor import ContainerCollector, PeersCollector
from dadvisor.analyzer.dataflow_cache import DataFlowCache
from dadvisor.config import TRAFFIC_SAMPLE
from dadvisor.datatypes.dataflow import DataFlow


class Analyzer(object):

    def __init__(self, container_collector: ContainerCollector, peers_collector: PeersCollector, loop):
        container_collector.analyser_thread = self
        self.container_collector = container_collector
        self.peers_collector = peers_collector
        self.loop = loop
        self.port_mapping: Dict[int, str] = {}  # a dict from port to container IP
        self.counter = Counter('bytes_send', 'Number of bytes send between two nodes', ['src', 'dst'])
        self.cache = DataFlowCache(self.counter)

        self.ports: OrderedDict[int, str] = OrderedDict()  # Contains at most TRAFFIC_SAMPLE elements

    async def analyse_dataflow(self, dataflow: DataFlow):
        """
        :param dataflow: the DataFlow-object to be analysed
        """

        self.add_port(dataflow.src)
        self.add_port(dataflow.dst)

        if dataflow.src.is_local() and dataflow.dst.is_local():
            src_hash = self.container_collector.ip_to_hash(dataflow.src.container)
            dst_hash = self.container_collector.ip_to_hash(dataflow.dst.container)
            if src_hash and dst_hash:
                self.counter.labels(src=src_hash, dst=dst_hash).inc(dataflow.size)
        elif not dataflow.dst.is_local():
            # src is local
            # dst is not local
            src_hash = self.container_collector.ip_to_hash(dataflow.src.container)
            peer = self.peers_collector.is_other_peer(dataflow.dst.host)
            if peer:
                self.cache.add_to(peer[0], src_hash, dataflow.dst.port, dataflow.size)
        elif not dataflow.src.is_local():
            # src is not local
            # dst is local
            dst_hash = self.container_collector.ip_to_hash(dataflow.dst.container)
            peer = self.peers_collector.is_other_peer(dataflow.src.host)
            if peer:
                self.cache.add_from(peer[0], dataflow.src.port, dst_hash, dataflow.size)

    def add_port(self, address):
        if address.is_local():
            while len(self.ports) >= int(TRAFFIC_SAMPLE):
                del self.ports[next(self.ports.__iter__())]
            self.ports[address.port] = address.container
