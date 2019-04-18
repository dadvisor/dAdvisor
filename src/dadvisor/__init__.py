import asyncio

from dadvisor.analyser import AnalyserThread
from dadvisor.containers import ContainerCollector
from dadvisor.inspector import InspectorThread
from dadvisor.peers import PeersCollector
from dadvisor.web import run_app, get_app
from dadvisor.log import log


def run_forever():
    """ Starts the program and creates all tasks """
    loop = asyncio.new_event_loop()

    # Create objects and threads
    peers_collector = PeersCollector()
    container_collector = ContainerCollector(peers_collector)

    inspector_thread = InspectorThread(peers_collector)
    analyser_thread = AnalyserThread(inspector_thread, container_collector, peers_collector)

    # Start threads
    inspector_thread.start()
    analyser_thread.start()

    # Create tasks
    app = get_app(loop, peers_collector)
    loop.create_task(run_app(app))
    loop.create_task(container_collector.run())
    loop.create_task(peers_collector.run())

    try:
        log.info('Running forever')
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('Stopping loop')
    finally:
        loop.close()
