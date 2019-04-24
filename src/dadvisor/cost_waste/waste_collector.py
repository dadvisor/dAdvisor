from prometheus_client import Counter

from dadvisor.log import log
from dadvisor.config import GB_PRICE_SECOND, gb_to_bytes, CPU_PRICE_SECOND
from dadvisor.containers.cadvisor import get_storage_info
from dadvisor.containers.prometheus import get_cpu_stat


class WasteCollector(object):

    def __init__(self, peers_collector):
        self.peers_collector = peers_collector
        self.counter = Counter('computational_waste_dollar', 'Waste in dollars of this host', ['host'])

    async def collect_waste(self, elapsed):
        total = await self.collect_computational_waste(elapsed) + await self.collect_memory_waste(elapsed)
        self.counter.labels(self.peers_collector.my_peer.host).inc(total)

    @staticmethod
    async def collect_computational_waste(elapsed_time):
        data = await get_cpu_stat()
        log.info(data)
        num_cores = data['data']['result'][0]['value'][1]
        log.info(num_cores)
        return CPU_PRICE_SECOND * num_cores * elapsed_time

    @staticmethod
    async def collect_memory_waste(elapsed_time):
        info = await get_storage_info()
        memory = sum([fs['usage'] for fs in info if fs['device'].startswith('/dev/')])

        return GB_PRICE_SECOND * gb_to_bytes(memory) * elapsed_time
