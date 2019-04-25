from prometheus_client import Counter

from dadvisor.log import log
from dadvisor.config import GB_PRICE_SECOND, gb_to_bytes, CPU_PRICE_SECOND
from dadvisor.containers.cadvisor import get_storage_info
from dadvisor.containers.prometheus import get_cpu_stat


class WasteCollector(object):

    def __init__(self):
        self.counter = Counter('computational_waste_dollar', 'Waste in dollars of this host')

    async def collect_waste(self, info, elapsed):
        total = await self.collect_computational_waste(info, elapsed) + await self.collect_memory_waste(elapsed)
        self.counter.inc(total)

    @staticmethod
    async def collect_computational_waste(info, elapsed_time):
        data = await get_cpu_stat()
        cores_used = float(data['data']['result'][0]['value'][1])
        cores_unused = info['num_cores'] - cores_used
        if cores_unused < 0:
            log.warn('Number of cores: {}'.format(info['num_cores']))
            log.warn('Cores unused: {}'.format(cores_unused))
            cores_unused = abs(cores_unused)
        return CPU_PRICE_SECOND * cores_unused * elapsed_time

    @staticmethod
    async def collect_memory_waste(elapsed_time):
        info = await get_storage_info()
        memory = sum([fs['usage'] for fs in info if fs['device'].startswith('/dev/')])

        return GB_PRICE_SECOND * gb_to_bytes(memory) * elapsed_time
