from prometheus_client import Counter

from dadvisor import ContainerCollector, PeersCollector
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
        :param dataflow: the dataflow-object to be analysed
        """

        self.add_port(dataflow.src)
        self.add_port(dataflow.dst)

        log.info(dataflow)
        src_hash = None
        dst_hash = None

        if dataflow.src.is_local():
            src_hash = self.container_collector.ip_to_hash(dataflow.src.container)
        else:
            pass  # Add to some kind of todo list

        if dataflow.dst.is_local():
            dst_hash = self.container_collector.ip_to_hash(dataflow.dst.container)
        else:
            pass  # Add to some kind of todo list

        if src_hash and dst_hash:
            log.debug('Found dataflow: {}'.format(dataflow))
            log.debug('src: {}, dst: {}'.format(src_hash, dst_hash))
            self.counter.labels(src=src_hash, dst=dst_hash).inc(dataflow.size)

    def add_port(self, address):
        if address.is_local():
            self.port_mapping[address.port] = self.container_collector.ip_to_hash(address.container)

    # def resolve_local_address(self, address):
    #     if address.host == INTERNAL_IP:
    #         for info in self.container_collector.containers:
    #             for port_map in info.ports:
    #                 if 'PublicPort' in port_map and str(port_map['PublicPort']) == str(address.port):
    #                     address.container = info.ip
    #                     if 'PrivatePort' in port_map:
    #                         address.port = str(port_map['PrivatePort'])
    #                     return
    #
    # async def resolve_remote_address(self, address):
    #     if address.host != INTERNAL_IP:
    #         p = self.peers_collector.get_peer_from_host(address.host)
    #         if p:
    #             ports = await get_ports(p)
    #             if address.port in ports:
    #                 address.container = ports[address.port]
