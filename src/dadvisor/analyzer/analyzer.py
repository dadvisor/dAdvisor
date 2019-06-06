from prometheus_client import Counter

from dadvisor import ContainerCollector, PeersCollector
from dadvisor.analyzer.dataflow_cache import DataFlowCache
from dadvisor.datatypes.dataflow import DataFlow
from dadvisor.log import log


class Analyzer(object):

    def __init__(self, container_collector: ContainerCollector, peers_collector: PeersCollector, loop):
        container_collector.analyser_thread = self
        self.container_collector = container_collector
        self.peers_collector = peers_collector
        self.loop = loop
        self.port_mapping = {}  # a dict from port to container_id
        self.counter = Counter('bytes_send', 'Number of bytes send between two nodes', ['src', 'dst'])
        self.cache = DataFlowCache()

    async def analyse_dataflow(self, dataflow: DataFlow):
        """
        In order to reduce the amount of http requests that is made to other peers,
        this function starts to sleep CACHE_TIME seconds. By doing this in an asynchronous
        manner, there is almost no overhead for the program itself.
        The flow for analysing a dataflow is the following:
            1. Add the ports from the source and destination to its own port mapping.
               Note that this is only done if the address is local.
            2. In case an other peers wants to analyse the port mapping, then this new
               port mapping is already returned. (Therefore, it is performed before sleeping.)
            3. The local host address is mapped from internal IP to external IP. Also, in case
               of a port mapping, the port is mapped from public to private (external to internal).
            4. In case the address is from a remote address, retrieve the container from the other peer.
            5. Increment the label from the local/remote source to the local/remote destination.
            6. The data is exposed as a prometheus_client-counter, such that the prometheus server scrapes
               this and stores this in its database.
        :param dataflow: the DataFlow-object to be analysed
        """

        self.add_port(dataflow.src)
        self.add_port(dataflow.dst)

        if dataflow.src.is_local() and dataflow.dst.is_local():
            src_hash = self.container_collector.ip_to_hash(dataflow.src.container)
            dst_hash = self.container_collector.ip_to_hash(dataflow.dst.container)
            if src_hash and dst_hash:
                log.info('Found dataflow: {}'.format(dataflow))
                self.counter.labels(src=src_hash, dst=dst_hash).inc(dataflow.size)
        elif not dataflow.dst.is_local():
            # src is local
            # dst is not local
            src_hash = self.container_collector.ip_to_hash(dataflow.src.container)
            peer = self.peers_collector.is_other_peer(dataflow.dst.host)
            if peer:
                self.cache.add_to(peer[0], src_hash, dataflow.dst.port, dataflow.size)
            else:
                log.info('Dropping (1) {}'.format(dataflow))
        elif not dataflow.src.is_local():
            # src is not local
            # dst is local
            dst_hash = self.container_collector.ip_to_hash(dataflow.dst.container)
            peer = self.peers_collector.is_other_peer(dataflow.src.host)
            if peer:
                self.cache.add_from(peer[0], dataflow.src.port, dst_hash, dataflow.size)
            else:
                log.info('Dropping (2) {}'.format(dataflow))

    def add_port(self, address):
        if address.is_local():
            self.port_mapping[address.port] = address.container
