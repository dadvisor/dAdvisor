import asyncio
from datetime import datetime, timedelta

from prometheus_client import Gauge, Counter
import numpy as np

from dadvisor.containers.prometheus import get_container_utilization
from dadvisor.log import log


class WasteCollector(object):
    """
    Collect information about other peers. The dAdvisor needs to be fully connected, as it needs to communicate with
    other peers if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self):
        self.waste_container = Gauge('waste_container', 'Waste utilization for a container', ['id'])
        self.waste_container_sum = Counter('waste_container', 'Total waste utilization for a container', ['id'])

    async def run(self):
        while True:
            try:
                now = datetime.utcnow()
                next_hour = now.replace(minute=0, second=20) + timedelta(hours=1)
                sleep_time = (next_hour - now).seconds
                await asyncio.sleep(sleep_time)
                # Execute once per hour (in the first minute)
                await self.compute_waste()
            except Exception as e:
                log.error(e)

    async def compute_waste(self):
        info = await get_container_utilization()
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
        n = len(util_list)
        if n == 0:
            return []  # return empty list if there is nothing to compute

        total_util = sum(util_list)
        total_waste = 1 - total_util

        A = np.zeros((n, n))
        for i in range(n - 1):
            A[i][0] = util_list[0]
            A[i][i + 1] = -util_list[i + 1]
            A[n - 1][i] = 1
        A[n - 1][n - 1] = 1

        b = np.zeros(n)
        b[n - 1] = total_waste
        return np.linalg.solve(A, b).tolist()


