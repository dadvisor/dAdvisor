import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from datatypes.address import IP
from datatypes.encoder import JSONCustomEncoder


def create_web_app(container_thread, inspector_thread, peers_thread, analyser_thread):
    app = Flask(__name__)
    app.json_encoder = JSONCustomEncoder
    CORS(app)

    @app.route('/containers')
    def containers():
        return jsonify([c.get_dict() for c in container_thread.containers_filtered])

    @app.route('/containers/all')
    def containers_all():
        return jsonify([c.get_dict() for c in container_thread.get_all_containers()])

    @app.route('/inspect')
    def inspect():
        return jsonify(analyser_thread.data)

    @app.route('/ip')
    def ip():
        return IP

    @app.route('/graph')
    def graph():
        return render_template('index.html')

    @app.route('/data')
    def data():
        hash_length = 12
        return jsonify({
            'nodes': container_thread.get_nodes(hash_length),
            'edges': inspector_thread.get_edges(container_thread, hash_length)
        })

    @app.route('/full_graph')
    def full_graph():
        nodes = []
        edges = []
        for p in peers_thread.peers:
            json = requests.get('http://{}:{}/data'.format(p.host, p.port)).json()
            nodes += json['nodes']
            edges += json['edges']
        return jsonify({'nodes': nodes, 'edges': edges})

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

    return app
