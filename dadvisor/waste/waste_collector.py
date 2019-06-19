import asyncio
from datetime import datetime, timedelta

from prometheus_client import Gauge, Counter

from dadvisor.nodes.node_actions import get_container_utilization, get_container_stats
from dadvisor.log import log


class WasteCollector(object):
    """
    Collect information about other nodes. The dAdvisor needs to be fully connected, as it needs to communicate with
    other nodes if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self, node_collector, container_collector):
        self.running = True
        self.node_collector = node_collector
        self.container_collector = container_collector

        self.util_container = Gauge('util_container', 'Utilization for a container', ['id'])
        self.util_container_sum = Counter('util_container', 'Total utilization for a container', ['id'])

        self.network_container = Gauge('network_container', 'Total amount of outgoing network', ['id'])

        self.waste_container = Gauge('waste_container', 'Waste utilization for a container', ['id'])
        self.waste_container_sum = Counter('waste_container', 'Total waste utilization for a container', ['id'])

    async def run(self):
        while self.running:
            try:
                now = datetime.utcnow()
                # next_hour = now.replace(minute=0, second=20) + timedelta(hours=1)
                next_hour = now + timedelta(minutes=1)
                sleep_time = (next_hour - now).seconds
                await asyncio.sleep(sleep_time)
                # Execute once per hour (in the first minute)
                await self.compute_network_usage()
                await self.compute_waste()

            except Exception as e:
                log.error(e)
        log.info('WasteCollector stopped')

    async def compute_network_usage(self):
        data = await get_container_stats()
        try:
            containers = [docker_id[len('/docker/'):] for docker_id in data.keys()]
            network_values = [self.get_network(value) for value in data.values()]
            self.filter_dadvisor(containers, network_values)
            for i, container in enumerate(containers):
                self.network_container.labels(container).set(network_values[i])
        except Exception as e:
            log.error(e)

    async def compute_waste(self):
        info = await get_container_utilization()
        try:
            containers = [docker_id[len('/docker/'):] for docker_id in info.keys()]
            util_list = [self.get_util(value) for value in info.values()]
            self.filter_dadvisor(containers, util_list)
        except Exception as e:
            log.error(e)
            return

        s = sum(util_list)
        if s > 1:
            log.info(f'Scaling utilization: {util_list}')
            for i, item in enumerate(util_list):
                util_list[i] = item / s

        waste_list = self.get_waste(util_list)
        log.info(f'Util: {util_list}')
        log.info(f'Waste: {waste_list}')
        for i, container in enumerate(containers):
            self.util_container.labels(container).set(util_list[i])
            self.util_container_sum.labels(container).inc(util_list[i])

            self.waste_container.labels(container).set(waste_list[i])
            self.waste_container_sum.labels(container).inc(waste_list[i])

    def filter_dadvisor(self, containers, values):
        try:
            dadvisor_index = containers.index(self.container_collector.dadvisor_id)
            del containers[dadvisor_index]
            del values[dadvisor_index]
        except ValueError:
            log.error(f'dadvisor_id unkown: {self.container_collector.dadvisor_id}')

    @staticmethod
    def get_network(value):
        amount = 0
        for row in value:
            try:
                network = row['network']
                interfaces = network['interfaces']
                amount += sum(interface['tx_bytes'] for interface in interfaces)
            except Exception as e:
                log.error(e)
        return amount

    def get_util(self, value):
        try:
            cores = self.node_collector.my_node_stats.get('num_cores', 1)
            return value['hour_usage']['cpu']['mean'] / (cores * 1000.0)
        except Exception as e:
            log.error(e)
            log.error(value)
            return 0

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
