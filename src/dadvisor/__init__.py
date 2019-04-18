import asyncio

from dadvisor.inspector import Inspector
from dadvisor.peers import PeersCollector
from dadvisor.web import run_app, get_app
from dadvisor.log import log


def run_forever():
    """ Starts the program and creates all tasks """
    loop = asyncio.new_event_loop()

    # Create objects
    peers_collector = PeersCollector()
    inspector = Inspector(peers_collector)

    # Create tasks
    app = get_app(loop, peers_collector)
    loop.create_task(run_app(app))
    # loop.create_task(inspector.run())
    loop.create_task(peers_collector.run())

    try:
        log.info('Running forever')
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('Stopping loop')
    finally:
        loop.close()
