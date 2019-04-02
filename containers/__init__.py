from log import log
from .thread import ContainerThread


def start_container_thread(peers_thread):
    log.info('Starting container thread')
    t = ContainerThread(peers_thread)
    t.start()
    return t
