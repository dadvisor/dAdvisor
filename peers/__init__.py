from log import log
from peers.thread import PeersThread


def start_peers_thread(port):
    log.info('Starting peers thread')
    t = PeersThread(port)
    t.start()
    return t
