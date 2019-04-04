import os

from stem.control import Controller
from werkzeug.serving import run_simple

from analyser import start_analyser_thread
from containers import create_container_thread
from inspector import start_inspector_thread
from log import log
from peers import start_peers_thread
from web import create_web_app

PORT = os.environ.get('PORT', '8800')

if __name__ == '__main__':
    peers_thread = start_peers_thread()
    container_thread = create_container_thread(peers_thread)
    inspector_thread = start_inspector_thread(peers_thread)
    analyser_thread = start_analyser_thread(inspector_thread, container_thread, peers_thread)
    container_thread.analyser_thread = analyser_thread
    container_thread.start()

    app = create_web_app(container_thread, peers_thread, inspector_thread, analyser_thread)
    host = "0.0.0.0"
    controller = Controller.from_port(port=9051)
    try:
        controller.authenticate()
        controller.set_options([
            ("HiddenServiceDir", "/etc/tor/temp"),
            ("HiddenServicePort", "80 %s:%s" % (host, str(PORT)))
        ])
        svc_name = open("etc/tor/temp/hostname", "r").read().strip()
        peers_thread.set_my_peer(svc_name)
    except Exception as e:
        print(e)

    run_simple(host, int(PORT), app, use_reloader=False)
    log.info('Stopping program')
