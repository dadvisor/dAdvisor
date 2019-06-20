import asyncio
import atexit

from dadvisor.nodes import NodeCollector
from dadvisor.containers import ContainerCollector
from dadvisor.analyzer import Analyzer
from dadvisor.inspector import InspectorThread
from dadvisor.log import log
from dadvisor.nodes.node_actions import remove_node
from dadvisor.stats import StatsCollector
from dadvisor.web import get_app, run_app


def run_forever():
    """ Starts the program and creates all tasks """
    loop = asyncio.new_event_loop()

    # Create objects and threads
    node_collector = NodeCollector(loop)
    container_collector = ContainerCollector()
    traffic_analyzer = Analyzer(container_collector, node_collector, loop)
    inspector_thread = InspectorThread(node_collector, traffic_analyzer)
    stats_collector = StatsCollector(node_collector, container_collector)

    app = get_app(loop, node_collector, traffic_analyzer, container_collector)

    # Start threads
    inspector_thread.start()

    # Create tasks
    loop.create_task(node_collector.set_my_node_stats())
    loop.create_task(run_app(app))
    loop.create_task(node_collector.run())
    loop.create_task(container_collector.run())
    loop.create_task(stats_collector.run())

    @atexit.register
    def on_exit():
        log.info('Stopping loop')
        remove_node(loop, node_collector.my_node)

    log.info('Started and running')
    loop.run_forever()
