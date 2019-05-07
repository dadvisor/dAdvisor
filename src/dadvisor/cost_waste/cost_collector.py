import asyncio

from prometheus_client import Gauge

from dadvisor.containers.prometheus import get_container_utilization

SLEEP_TIME = 5


class CostCollector(object):

    def __init__(self):
        """
        The CostCollector also creates the WasteCollector, as both are related and
        implement pretty much the same logic. They both store their data in a
        prometheus_client-Counter, such that the prometheus server scrapes this data.

        This also keeps track of the amount of elapsed seconds, which is used in the computation.
        """
        self.gauge = Gauge('container_utilization', 'Utilization (in percentage) of a certain container', ['id'])

    async def run(self):
        while True:
            await asyncio.sleep(SLEEP_TIME)

            info = await get_container_utilization()
            await self.store_utilization(info)

    async def store_utilization(self, info):
        for container in info['data']['result']:
            name = container['metric']['id'][len('/docker/'):]
            self.gauge.labels(name).set(float(container['value'][1]))
