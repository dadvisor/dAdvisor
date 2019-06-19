from typing import Dict, List, Tuple

from dadvisor.log import log
from dadvisor.nodes.node_actions import get_ports, get_container_mapping

FROM = 0
TO = 1


class DataFlowCache(object):
    """
        implements a caching functionality, such that multiple addresses can be resolved at once.
    """

    def __init__(self, counter):
        self.cache: Dict[str, List[Tuple[int, str, int, int]]] = {}
        self.counter = counter

    def add_to(self, ip: str, from_hash: str, to_port: int, size: int):
        data = (TO, from_hash, to_port, size)
        self._add(ip, data)

    def add_from(self, ip: str, from_port: int, to_hash: str, size: int):
        data = (FROM, to_hash, from_port, size)
        self._add(ip, data)

    def _add(self, ip: str, data: Tuple[int, str, int, int]):
        if ip not in self.cache:
            self.cache[ip] = [data]
        else:
            self.cache[ip].append(data)

    async def resolve(self, nodes_collector):
        """
        Ask all nodes to resolve their ports into a container-hash.
        After this function has been called, the cache is empty
        """
        for ip, data_list in list(self.cache.items()):

            node = nodes_collector.is_other_node(ip)
            if not node:
                continue

            try:
                ports = await get_ports(node)
                # port is encoded as string, therefore decode to int
                ports = {int(port): ip for port, ip in ports.items()}
                containers = await get_container_mapping(node)

                for (from_to, local_hash, port, size) in data_list:
                    remote_hash = None
                    if port in ports:
                        ip = ports[port]
                        if ip in containers:
                            remote_hash = containers[ip]
                    if local_hash and remote_hash:
                        if from_to == TO:
                            self.counter.labels(src=local_hash, dst=remote_hash).inc(size)
                        elif from_to == FROM:
                            self.counter.labels(src=remote_hash, dst=local_hash).inc(size)
                del self.cache[ip]
            except Exception as e:
                log.error(e)
        self.cache = {}
