from log import log
from peers.thread import PeersThread


def start_peers_thread():
    log.info('Starting peers thread')
    t = PeersThread()
    t.start()
    return t
