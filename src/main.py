from werkzeug.serving import run_simple

from dadvisor.analyser import AnalyserThread
from dadvisor.config import PORT
from dadvisor.containers import ContainerThread
from dadvisor.inspector import InspectorThread
from dadvisor.peers import PeersThread
from dadvisor.web import create_web_app

HOST = '0.0.0.0'

if __name__ == '__main__':
    peers_thread = PeersThread()
    container_thread = ContainerThread(peers_thread)
    inspector_thread = InspectorThread(peers_thread)
    analyser_thread = AnalyserThread(inspector_thread, container_thread, peers_thread)
    container_thread.analyser_thread = analyser_thread

    app = create_web_app(container_thread, peers_thread, inspector_thread, analyser_thread)

    peers_thread.start()
    container_thread.start()
    inspector_thread.start()
    analyser_thread.start()

    run_simple(HOST, PORT, app, use_reloader=False)
