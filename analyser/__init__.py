from analyser.thread import AnalyserThread


def start_analyser_thread(inspector_thread, container_thread):
    print('Starting analyser thread')
    t = AnalyserThread(inspector_thread, container_thread)
    t.start()
    return t