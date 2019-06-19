import asyncio
import signal
import sys

from dadvisor.nodes import NodeCollector
from dadvisor.containers import ContainerCollector
from dadvisor.analyzer import Analyzer
from dadvisor.inspector import InspectorThread
from dadvisor.log import log
from dadvisor.waste import WasteCollector
from dadvisor.web import get_app, run_app


def run_forever():
    """ Starts the program and creates all tasks """

    def signal_handler(signal, frame):
        loop.stop()
        log.info('Stopping loop')
        loop.create_task(node_collector.stop())
        inspector_thread.stop()
        container_collector.stop()
        waste_collector.stop()
        sys.exit(0)

    loop = asyncio.new_event_loop()

    # Create objects and threads
    node_collector = NodeCollector(loop)
    container_collector = ContainerCollector()
    traffic_analyzer = Analyzer(container_collector, node_collector, loop)
    inspector_thread = InspectorThread(node_collector, traffic_analyzer)
    waste_collector = WasteCollector(node_collector)

    app = get_app(loop, node_collector, traffic_analyzer, container_collector)

    # Start threads
    inspector_thread.start()

    # Create tasks
    loop.create_task(node_collector.set_my_node_stats())
    loop.create_task(run_app(app))
    loop.create_task(node_collector.run())
    loop.create_task(container_collector.run())
    loop.create_task(waste_collector.run())

    log.info('Started and running')
    signal.signal(signal.SIGINT, signal_handler)

    loop.run_forever()
