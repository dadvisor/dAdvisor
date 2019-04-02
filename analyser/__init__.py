from analyser.thread import AnalyserThread
from log import log


def start_analyser_thread(inspector_thread, container_thread, peers_thread):
    log.info('Starting analyser thread')
    t = AnalyserThread(inspector_thread, container_thread, peers_thread)
    t.start()
    return t
