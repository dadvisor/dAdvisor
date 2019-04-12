import os

from werkzeug.serving import run_simple

from .analyser import AnalyserThread
from .containers import ContainerThread
from .inspector import InspectorThread
from .peers import PeersThread
from .web import create_web_app

PORT = os.environ.get('PORT', '8800')
HOST = '0.0.0.0'

if __name__ == '__main__':
    peers_thread = PeersThread()
    container_thread = ContainerThread(peers_thread)
    inspector_thread = InspectorThread(peers_thread)
    analyser_thread = AnalyserThread(inspector_thread, container_thread, peers_thread)
    container_thread.analyser_thread = analyser_thread

    app = create_web_app(container_thread, peers_thread, inspector_thread, analyser_thread)

    peers_thread.set_my_peer(PORT)
    peers_thread.start()
    container_thread.start()
    inspector_thread.start()
    analyser_thread.start()

    run_simple(HOST, int(PORT), app, use_reloader=False)
