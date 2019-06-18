import asyncio
from datetime import datetime, timedelta

from prometheus_client import Gauge, Counter

from dadvisor.containers.cadvisor import get_container_utilization
from dadvisor.log import log


class WasteCollector(object):
    """
    Collect information about other peers. The dAdvisor needs to be fully connected, as it needs to communicate with
    other peers if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self):
        self.running = True
        self.waste_container = Gauge('waste_container', 'Waste utilization for a container', ['id'])
        self.waste_container_sum = Counter('waste_container', 'Total waste utilization for a container', ['id'])

    async def run(self):
        while self.running:
            try:
                now = datetime.utcnow()
                next_hour = now.replace(minute=0, second=20) + timedelta(hours=1)
                sleep_time = (next_hour - now).seconds
                await asyncio.sleep(sleep_time)
                # Execute once per hour (in the first minute)
                await self.compute_waste()
            except Exception as e:
                log.error(e)
        log.info('WasteCollector stopped')

    async def compute_waste(self):
        info = await get_container_utilization()
        containers = info.keys()
        print(containers)
        # TODO: parse data

        util_list = [float(container['value'][1]) for container in info['data']['result']]
        waste_list = self.get_waste(util_list)
        log.info('Computing waste: {}'.format(util_list))
        for i, container in enumerate(info['data']['result']):
            name = container['metric']['id'][len('/docker/'):]
            self.waste_container.labels(name).set(waste_list[i])
            self.waste_container_sum.labels(name).inc(waste_list[i])

    @staticmethod
    def get_waste(util_list):
        """
        :return: A list of the waste per container, in the same order as the given util_list
        """
        waste_list = []
        for u_i in util_list:
            waste_list.append(max(1 / len(util_list) - u_i, 0))

        u = sum(util_list)
        w = sum(waste_list)

        if u + w != 1:
            for i, elem in enumerate(waste_list):
                waste_list[i] = elem * (1 - u) / w
        return waste_list

    def stop(self):
        self.running = False
        log.info('Stopping WasteCollector')
