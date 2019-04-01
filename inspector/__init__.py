from inspector.thread import InspectorThread


def start_inspector_thread(peers_thread):
    print('Starting inspector thread')
    t = InspectorThread(peers_thread)
    t.start()
    return t
