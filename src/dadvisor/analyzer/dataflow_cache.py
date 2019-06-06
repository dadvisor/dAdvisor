from typing import Dict, List, Tuple

from dadvisor.log import log
from dadvisor.datatypes.peer import Peer
from dadvisor.peers.peer_actions import get_ports, get_container_mapping

FROM = 0
TO = 1


class DataFlowCache(object):
    """
        implements a caching functionality, such that multiple addresses can be resolved at once.
    """

    def __init__(self, counter):
        self.cache: Dict[Peer, List[Tuple[int, str, int, int]]] = {}
        self.counter = counter

    def add_to(self, peer: Peer, from_hash: str, to_port: int, size: int):
        data = (TO, from_hash, to_port, size)
        self._add(peer, data)

    def add_from(self, peer: Peer, from_port: int, to_hash: str, size: int):
        data = (FROM, to_hash, from_port, size)
        self._add(peer, data)

    def _add(self, peer: Peer, data: Tuple[int, str, int, int]):
        if peer not in self.cache:
            self.cache[peer] = [data]
        else:
            self.cache[peer].append(data)

    async def resolve(self):
        """
        Ask all peers to resolve their ports into a container-hash.
        After this function has been called, the cache is empty
        """
        for peer, data_list in list(self.cache.items()):
            ports = await get_ports(peer)
            containers = await get_container_mapping(peer)
            log.info(ports)
            log.info(containers)

            for (from_to, local_hash, port, size) in data_list:
                try:
                    ip = ports[port]
                    remote_hash = containers[ip]
                except Exception as e:
                    log.error(e)
                    continue
                if from_to == TO:
                    self.counter.labels(src=local_hash, dst=remote_hash).inc(size)
                elif from_to == FROM:
                    self.counter.labels(src=remote_hash, dst=local_hash).inc(size)

            del self.cache[peer]
        self.cache = {}
