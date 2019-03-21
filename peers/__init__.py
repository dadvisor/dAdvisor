from peers.thread import PeersThread


def start_peers_thread():
    t = PeersThread()
    t.start()
    return t
