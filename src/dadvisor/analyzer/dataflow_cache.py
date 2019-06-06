from typing import Dict, List, Tuple

from dadvisor.log import log
from dadvisor.datatypes.peer import Peer

FROM = 0
TO = 1


class DataFlowCache(object):
    """
        implements a caching functionality, such that multiple addresses can be resolved at once.
    """

    def __init__(self):
        self.cache: Dict[Peer, List[Tuple[int, str, int, int]]] = {}

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

    def resolve(self):
        """
        Ask all peers to resolve their ports into a container-hash.
        After this function has been called, the cache is empty
        """
        for peer, data_list in self.cache.items():
            log.info('Peer {} contains {} items'.format(peer.host, len(data_list)))
            l2 = [port for (_, _, port, _) in data_list]
            log.info('Ports: {}'.format(l2))

        self.cache = {}
