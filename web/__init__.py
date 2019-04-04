import logging

import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from datatypes.address import IP
from datatypes.encoder import JSONCustomEncoder
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app


def create_web_app(container_thread, peers_thread, inspector_thread, analyser_thread):
    app = Flask(__name__)
    app.json_encoder = JSONCustomEncoder
    CORS(app)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)

    @app.route('/containers')
    def containers():
        return jsonify(container_thread.containers_filtered)

    @app.route('/containers/all')
    def containers_all():
        return jsonify(container_thread.get_all_containers())

    @app.route('/ip')
    def ip():
        return IP

    @app.route('/size')
    def size():
        return jsonify(inspector_thread.data.qsize())

    @app.route('/graph')
    def graph():
        return render_template('index.html')

    @app.route('/data')
    def data():
        hash_length = 12
        nodes = container_thread.get_nodes(hash_length)
        edges = analyser_thread.get_edges()
        for p in peers_thread.other_peers:
            edges += requests.get('http://{}:{}/edges'.format(p.host, p.port)).json()
        container_thread.validate_edges(edges, nodes)

        return jsonify({
            'nodes': nodes,
            'edges': edges
        })

    @app.route('/edges')
    def get_edges():
        return jsonify(analyser_thread.get_edges())

    @app.route('/resolve_port/<port>')
    def resolve_port(port):
        return jsonify(analyser_thread.resolve_port(port))

    @app.route('/ports')
    def ports():
        return jsonify(analyser_thread.ports)

    @app.route('/peers')
    def peers():
        return jsonify(peers_thread.peers)

    @app.route('/peers/add/<host_port>')
    def peers_add(host_port):
        """
        :param host_port: Example: 35.204.153.106:8800
        :return: A json object with {'host': '35.204.153.106', 'port': '8800'}
        """
        host, port = host_port.split(':')
        p = peers_thread.add_peer(host, port)
        return jsonify(p)

    app = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })

    return app
