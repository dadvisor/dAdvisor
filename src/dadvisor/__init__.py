import asyncio

from dadvisor.analyzer import Analyzer
from dadvisor.containers import ContainerCollector
from dadvisor.inspector import InspectorThread
from dadvisor.log import log
from dadvisor.peers import PeersCollector
from dadvisor.waste import WasteCollector
from dadvisor.web import get_app, run_app


def run_forever():
    """ Starts the program and creates all tasks """
    loop = asyncio.new_event_loop()

    # Create objects and threads
    peers_collector = PeersCollector()
    container_collector = ContainerCollector(peers_collector)
    traffic_analyzer = Analyzer(container_collector, peers_collector, loop)
    inspector_thread = InspectorThread(peers_collector, traffic_analyzer)
    waste_collector = WasteCollector()

    app = get_app(loop, peers_collector, traffic_analyzer, container_collector)

    # Start threads
    inspector_thread.start()

    # Create tasks
    loop.create_task(run_app(app))
    loop.create_task(peers_collector.run())
    loop.create_task(container_collector.run())
    loop.create_task(waste_collector.run())

    try:
        log.info('Started and running')
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('Stopping loop')
    finally:
        loop.close()
