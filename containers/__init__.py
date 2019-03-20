from .thread import ContainerThread


def start_container_thread():
    print('Starting container thread')
    t = ContainerThread()
    t.start()
    return t
