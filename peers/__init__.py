from peers.thread import PeersThread


def start_peers_thread(port):
    print('Starting peers thread')
    t = PeersThread(port)
    t.start()
    return t
