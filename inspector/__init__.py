from inspector.thread import InspectorThread
from log import log


def start_inspector_thread(peers_thread):
    log.info('Starting inspector thread')
    t = InspectorThread(peers_thread)
    t.start()
    return t
