from inspector.thread import InspectorThread


def start_inspector_thread():
    print('Starting inspector thread')
    t = InspectorThread()
    t.start()
    return t
