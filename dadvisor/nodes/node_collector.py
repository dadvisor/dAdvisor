import asyncio
import json

from prometheus_client import Info

from dadvisor.config import IP, PROXY_PORT, IS_SUPER_NODE
from dadvisor.datatypes.node import Node
from dadvisor.log import log
from dadvisor.nodes.node_actions import register_node, remove_node, get_node_info, get_all_nodes, get_machine_info

FILENAME = '/prometheus.json'
SLEEP_TIME = 60

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
        self.set_my_node()
        self.set_scraper([])

    def set_my_node(self):
        num_cores, memory = self.loop.run_until_complete(get_machine_info())
        self.set_node_info(self.my_node, {
            'num_cores': num_cores,
            'memory': memory
        })

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
        succeeded = False
        while not succeeded:
            try:
                await register_node(self.loop, self.my_node)
                succeeded = True
            except Exception as e:
                log.error(e)

        while self.running:
            try:
                await asyncio.sleep(SLEEP_TIME)
                await self.set_nodes(await get_all_nodes())
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

    async def set_nodes(self, data_list):
        data = data_list['list']
        log.info(data)
        self.other_nodes = []
        for node_json in data:
            node_data = node_json['node']
            log.info(type(node_data['ip']))
            log.info(type(node_data['port']))
            log.info(type(node_data['is_super_node']))
            node = Node(node_data['ip'], int(node_data['port']), node_data['is_super_node'])
            if node == self.my_node:
                continue
            try:
                info = await get_node_info(node)
                await self.set_node_info(node, info)
                self.other_nodes.append(node)
            except Exception as e:
                log.error(e)

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
        await remove_node(self.loop, self.my_node)
