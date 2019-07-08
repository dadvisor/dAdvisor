from typing import Dict, List, Tuple

from dadvisor.config import IP
from dadvisor.log import log
from dadvisor.nodes.node_actions import get_mapping

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
                log.error('Node not found')
                continue

            try:
                mapping = await get_mapping(node)
                ports = mapping['ports']
                # port is encoded as string, therefore decode to int
                ports = {int(port): ip for port, ip in ports.items()}
                containers = mapping['containers']

                for (from_to, local_hash, port, size) in data_list:
                    ip = ports.get(port, None)
                    remote_hash = containers.get(ip, None)
                    if local_hash and remote_hash:
                        if from_to == TO:
                            self.counter.labels(src=local_hash, dst=remote_hash, src_host=IP)\
                                .inc(size)
                        elif from_to == FROM:
                            self.counter.labels(src=remote_hash, dst=local_hash, src_host=IP)\
                                .inc(size)
                try:
                    del self.cache[ip]
                except KeyError:
                    log.debug(f'Cannot remove {ip} from self.cache')
            except Exception as e:
                log.error(e)
        self.cache = {}
