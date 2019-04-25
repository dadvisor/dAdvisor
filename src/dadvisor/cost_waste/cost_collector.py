import asyncio
from datetime import datetime

from prometheus_client import Counter

from dadvisor.log import log
from dadvisor.config import CPU_PRICE_SECOND, GB_PRICE_SECOND, gb_to_bytes
from dadvisor.containers.cadvisor import get_machine_info
from dadvisor.cost_waste.waste_collector import WasteCollector

SLEEP_TIME = 15


class CostCollector(object):

    def __init__(self, container_collector):
        self.container_collector = container_collector
        self.waste_collector = WasteCollector()
        self.counter = Counter('computational_cost_dollar', 'Cost in dollar of providing this host')
        self.update_time = datetime.now()

    async def run(self):
        while True:
            await asyncio.sleep(SLEEP_TIME)

            # compute elapsed time (in seconds)
            update_time = datetime.now()
            elapsed = (update_time - self.update_time).seconds
            self.update_time = update_time

            info = await get_machine_info()
            await self.collect_cost(info, elapsed)
            await self.waste_collector.collect_waste(info, elapsed)

    async def collect_cost(self, info, elapsed):

        total = self.collect_computational_cost(info['num_cores'], elapsed) + self.collect_memory_cost(info, elapsed)
        if total < 0:
            log.warn('Collected cost cannot be negative: {}'.format(total))
            total = abs(total)
        self.counter.inc(total)

    @staticmethod
    def collect_computational_cost(num_cores, elapsed_time):
        return CPU_PRICE_SECOND * num_cores * elapsed_time

    @staticmethod
    def collect_memory_cost(info, elapsed_time):
        memory = sum([fs['capacity'] for fs in info['filesystems'] if fs['device'].startswith('/dev/')])
        return GB_PRICE_SECOND * gb_to_bytes(memory) * elapsed_time



