import asyncio
from datetime import datetime

from prometheus_client import Counter

from dadvisor.config import SLEEP_TIME, IP
from dadvisor.nodes.node_actions import get_container_utilization, get_container_stats
from dadvisor.log import log

FACTOR = SLEEP_TIME / 3600


class StatsCollector(object):
    """
    Collect information about other nodes. The dAdvisor needs to be fully connected, as it needs to communicate with
    other nodes if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self, node_collector, container_collector):
        self.running = True
        self.node_collector = node_collector
        self.container_collector = container_collector
        self.prev_network_container = {}

        self.network_container_sum = Counter('network_container', 'Total amount of outgoing network',
                                             ['src', 'src_host'])

        self.cpu_util_container_sum = Counter('cpu_util_container',
                                              'Total CPU utilization percentage for a container',
                                              ['src', 'src_host'])
        self.mem_util_container_sum = Counter('mem_util_container',
                                              'Total memory utilization percentage for a container',
                                              ['src', 'src_host'])

        self.cpu_waste_container_sum = Counter('cpu_waste_container',
                                               'Total CPU waste percentage for a container',
                                               ['src', 'src_host'])
        self.mem_waste_container_sum = Counter('mem_waste_container',
                                               'Total memory waste percentage for a container',
                                               ['src', 'src_host'])

    async def run(self):
        elapsed = 0
        while self.running:
            try:
                await asyncio.sleep(SLEEP_TIME - elapsed)
                now = datetime.utcnow()
                log.info(f'Sleeping {SLEEP_TIME - elapsed} sec')
                # Execute once per SLEEP_TIME
                await self.compute_network_usage()
                await self.compute_util_and_waste()
                now2 = datetime.utcnow()
                elapsed = (now2 - now).seconds

            except Exception as e:
                log.error(e)
        log.info('StatsCollector stopped')

    async def compute_network_usage(self):
        data = await get_container_stats()
        try:
            containers = [docker_id[len('/docker/'):] for docker_id in data.keys()]
            network_values = [self.get_network(value) for value in data.values()]
            self.filter_dadvisor(containers, network_values)
            for i, container in enumerate(containers):
                prev = self.prev_network_container.get(container, 0)
                log.info(f'Container {container}: {prev}')
                self.prev_network_container[container] = network_values[i]
                self.network_container_sum.labels(src=container, src_host=IP)\
                    .inc(network_values[i] - prev)
        except Exception as e:
            log.error(e)

    async def compute_util_and_waste(self):
        info = await get_container_utilization()
        try:
            containers = [docker_id[len('/docker/'):] for docker_id in info.keys()]
            util_list = [self.get_util(value) for value in info.values()]
            self.filter_dadvisor(containers, util_list)
        except Exception as e:
            log.error(e)
            return

        if not util_list:
            return

        cpu_util_list, mem_util_list = zip(*util_list)

        self.scale_list(cpu_util_list)
        self.scale_list(mem_util_list)

        cpu_waste_list = self.get_waste(cpu_util_list)
        mem_waste_list = self.get_waste(mem_util_list)

        log.info(cpu_util_list)

        for i, container in enumerate(containers):
            self.cpu_util_container_sum.labels(src=container, src_host=IP)\
                .inc(cpu_util_list[i] * FACTOR)
            self.mem_util_container_sum.labels(src=container, src_host=IP)\
                .inc(mem_util_list[i] * FACTOR)
            self.cpu_waste_container_sum.labels(src=container, src_host=IP)\
                .inc(cpu_waste_list[i] * FACTOR)
            self.mem_waste_container_sum.labels(src=container, src_host=IP)\
                .inc(mem_waste_list[i] * FACTOR)

    def filter_dadvisor(self, containers, values):
        """ Don't compute utilization values about dAdvisor """
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
            memory = self.node_collector.my_node_stats.get('memory', 8*2**30)
            cpu = value['minute_usage']['cpu']['mean'] / (cores * 1000.0)
            memory_percentage = value['minute_usage']['memory']['mean'] / memory
            return cpu, memory_percentage
        except Exception as e:
            log.error(e)
            return 0

    @staticmethod
    def scale_list(util_list):
        s = sum(util_list)
        if s > 1:
            log.info(f'Scaling list: {util_list}')
            for i, item in enumerate(util_list):
                util_list[i] = item / s

    @staticmethod
    def get_waste(util_list):
        """
        :return: A list of the stats per container, in the same order as the given util_list
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
