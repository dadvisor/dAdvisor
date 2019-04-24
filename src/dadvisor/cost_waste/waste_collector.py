from prometheus_client import Counter

from dadvisor.config import GB_PRICE_SECOND, gb_to_bytes, CPU_PRICE_SECOND
from dadvisor.containers.cadvisor import get_storage_info


class WasteCollector(object):

    def __init__(self, peers_collector):
        self.peers_collector = peers_collector
        self.counter = Counter('computational_waste_dollar', 'Waste in dollars of this host', ['host'])

    async def collect_waste(self, elapsed):
        info = await get_storage_info()

        total = self.collect_computational_waste(info['num_cores'], elapsed) + self.collect_memory_waste(info, elapsed)
        self.counter.labels(self.peers_collector.my_peer.host).inc(total)

    @staticmethod
    def collect_computational_waste(num_cores, elapsed_time):
        return CPU_PRICE_SECOND * num_cores * elapsed_time

    @staticmethod
    def collect_memory_waste(info, elapsed_time):
        memory = sum([fs['usage'] for fs in info if fs['device'].startswith('/dev/')])

        return GB_PRICE_SECOND * gb_to_bytes(memory) * elapsed_time
