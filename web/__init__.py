import json
import subprocess

import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

IP = requests.get('https://api.ipify.org').text


def create_web_app(container_thread, inspector_thread, peers_thread):
    app = Flask(__name__)
    CORS(app)

    @app.route('/containers')
    def containers():
        if request.args.get('filtered', default=False, type=bool):
            c = container_thread.containers_filtered()
        else:
            c = container_thread.containers
        return jsonify({k: v.get_dict() for k, v, in c.items()})

    @app.route('/inspect')
    def inspect():
        return jsonify(inspector_thread.data)

    @app.route('/inspect/<src>')
    def inspect_src(src):
        return jsonify(inspector_thread.inspect(src))

    @app.route('/ip')
    def ip():
        return IP

    @app.route('/api/<path:command>')
    def api(command):
        cmd = 'curl --unix-socket /var/run/docker.sock http://localhost' + request.full_path[4:]
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return jsonify(p.communicate()[0].decode('utf-8'))

    @app.route('/graph')
    def graph():
        return render_template('index.html')

    @app.route('/data')
    def data():
        hash_length = 12
        return jsonify({
            'nodes': container_thread.get_nodes(IP, hash_length),
            'edges': inspector_thread.get_edges(container_thread, hash_length)
        })

    @app.route('/peers')
    def peers():
        return jsonify([p.__dict__ for p in peers_thread.peers])

    @app.route('/peers/add/<host_port>')
    def peers_add(host_port):
        """
        :param host_port: Example: 35.204.153.106:8800
        :return: A json object with {'host': '35.204.153.106', 'port': '8800'}
        """
        host, port = host_port.split(':')
        p = peers_thread.add_peer(host, port)
        return jsonify(p.__dict__)

    return app
