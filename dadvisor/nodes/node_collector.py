import asyncio
import json

from prometheus_client import Info

from dadvisor.config import IP, PROXY_PORT, IS_SUPER_NODE
from dadvisor.datatypes.node import Node
from dadvisor.log import log
from dadvisor.nodes.node_actions import register_node, remove_node, get_node_info, get_all_nodes, get_machine_info

FILENAME = '/prometheus.json'
SLEEP_TIME = 60

CHECK_REMOVE = 10

NODE_INFO = Info('node', 'Nodes', ['host'])


class NodeCollector(object):
    """
    Collect information about other nodes. The dAdvisor needs to be fully connected, as it needs to communicate with
    other nodes if it detects a dataflow between its own peer and a remote peer.
    """

    def __init__(self, loop):
        self.loop = loop
        self.running = True
        self.my_node = Node(IP, PROXY_PORT, IS_SUPER_NODE)
        self.other_nodes = []
        self.set_scraper([])
        self.check_removal_counter = 0
        self.my_node_stats = {}

    async def set_my_node_stats(self):
        num_cores, memory = await get_machine_info()
        self.my_node_stats = {
            'num_cores': num_cores,
            'memory': memory
        }
        self.set_node_info(self.my_node, self.my_node_stats)

    @staticmethod
    def set_node_info(node: Node, data):
        NODE_INFO.labels(host=node.ip).info({
            'port': str(node.port),
            'num_cores': str(data['num_cores']),
            'memory': str(data['memory']),
            'is_super_node': str(node.is_super_node)})

    async def run(self):
        """
        This run method performs the following two actions:
        1. register this peer in the tracker
        2. continuously perform the following actions:
            - validate other nodes
        :return:
        """
        register_node(self.loop, self.my_node)

        while self.running:
            try:
                await asyncio.sleep(SLEEP_TIME)
                self.loop.create_task(self.add_nodes(await get_all_nodes()))
                self.check_removal_counter += 1
                if self.check_removal_counter == CHECK_REMOVE:
                    self.check_removal_counter = 0
                    self.loop.create_task(self.check_nodes())
            except Exception as e:
                log.error(e)

    @property
    def nodes(self):
        return [self.my_node] + self.other_nodes

    def is_other_node(self, ip):
        for node in self.other_nodes:
            if node.ip == ip:
                return node
        return None

    async def add_nodes(self, data_list):
        new_nodes = []
        found_my_node = False
        for node_json in data_list['list']:
            node_data = node_json['node']
            node = Node(node_data['ip'], int(node_data['port']), node_data['is_super_node'])

            if node == self.my_node:
                found_my_node = True
            elif node not in self.other_nodes:
                self.loop.create_task(self.set_node_info(node, await get_node_info(node)))
                new_nodes.append(node)

        if not found_my_node:
            register_node(self.loop, self.my_node)
        self.other_nodes += new_nodes

    async def check_nodes(self):
        """ Removes the nodes that cannot be reached """
        remove_nodes = []
        for node in self.other_nodes:
            info = await get_node_info(node)
            if not info:
                remove_nodes.append(node)
        for node in remove_nodes:
            self.other_nodes.remove(node)

    @staticmethod
    def set_scraper(nodes):
        """ Set a line with federation information. Prometheus is configured in
        such a way that it reads this file. """
        try:
            with open(FILENAME, 'r') as file:
                old_data = file.read()
        except FileNotFoundError:
            old_data = ''

        node_list = [f'localhost:{PROXY_PORT}']
        for node in nodes:
            node_list.append('{}:{}'.format(node.ip, node.port))

        data = [{"labels": {"job": "dadvisor"}, "targets": node_list}]
        new_data = json.dumps(data) + '\n'
        log.debug(new_data)

        if old_data != new_data:
            with open(FILENAME, 'w') as file:
                file.write(new_data)

    async def stop(self):
        self.running = False
        remove_node(self.loop, self.my_node)
