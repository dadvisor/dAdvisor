import os

from stem.control import Controller
from werkzeug.serving import run_simple

from .analyser import AnalyserThread
from .containers import ContainerThread
from .inspector import InspectorThread
from .log import log
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
    controller = Controller.from_port(port=9051)
    try:
        controller.authenticate()
        controller.set_options([
            ("HiddenServiceDir", "/etc/tor/temp"),
            ("HiddenServicePort", "80 %s:%s" % (HOST, str(PORT)))
        ])
        svc_name = open("etc/tor/temp/hostname", "r").read().strip()
        peers_thread.set_my_peer(svc_name)
        log.info('-' * 50)
        log.info(svc_name)
        log.info('-' * 50)

        peers_thread.start()
        container_thread.start()
        inspector_thread.start()
        analyser_thread.start()

        run_simple(HOST, int(PORT), app, use_reloader=False)
    except Exception as e:
        print(e)
