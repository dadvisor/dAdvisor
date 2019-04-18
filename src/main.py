from dadvisor import run_forever

HOST = '0.0.0.0'

if __name__ == '__main__':
    run_forever()
    # peers_thread = Peers()
    # container_thread = ContainerThread(peers_thread)
    # inspector_thread = InspectorThread(peers_thread)
    # analyser_thread = AnalyserThread(inspector_thread, container_thread, peers_thread)
    # container_thread.analyser_thread = analyser_thread
    #
    # app = create_web_app(container_thread, peers_thread, inspector_thread, analyser_thread)
    #
    # peers_thread.start()
    # container_thread.start()
    # inspector_thread.start()
    # analyser_thread.start()
    #
    # run_simple(HOST, PORT, app, use_reloader=False)
