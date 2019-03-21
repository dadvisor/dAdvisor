from containers import start_container_thread
from inspector import start_inspector_thread
from peers import start_peers_thread
from web import create_web_app


if __name__ == '__main__':
    container_thread = start_container_thread()
    inspector_thread = start_inspector_thread()
    peers_thread = start_peers_thread()

    app = create_web_app(container_thread, inspector_thread, peers_thread)
    app.run(debug=True, host='0.0.0.0', port=8800)

    print('Stopping program')
