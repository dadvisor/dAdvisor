from .thread import ContainerThread


def start_container_thread(peers_thread):
    print('Starting container thread')
    t = ContainerThread(peers_thread)
    t.start()
    return t
