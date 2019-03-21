from peers.thread import PeersThread


def start_peers_thread(port):
    t = PeersThread(port)
    t.start()
    return t
