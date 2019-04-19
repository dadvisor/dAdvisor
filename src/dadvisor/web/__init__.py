import json

import aiohttp
from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from dadvisor.log import log
from dadvisor.config import INTERNAL_IP, IP, PORT
from dadvisor.datatypes.encoder import JSONCustomEncoder


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    log.info('Running on localhost:{}'.format(PORT))
    await site.start()


def get_app(loop, peers_collector):
    async def metrics(request):
        resp = web.Response(body=generate_latest())
        resp.content_type = CONTENT_TYPE_LATEST
        return resp

    async def ip(request):
        return web.json_response({'internal': INTERNAL_IP, 'external': IP})

    async def hosts(request):
        return web.json_response(text=json.dumps(peers_collector.host_mapping,
                                                 cls=JSONCustomEncoder))

    async def peers(request):
        return web.json_response(text=json.dumps(peers_collector.peers,
                                                 cls=JSONCustomEncoder))

    async def prometheus(request):
        path = request.match_info['path']
        if not path.startswith('/'):
            path = '/' + path
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:9090{}'.format(path)) as resp:
                text = await resp.text()
                log.info(resp.status)
                log.info(str(resp.headers))
                log.info(text)
        return web.Response(text=text, status=resp.status, headers=resp.headers)

    async def add_peer(request):
        peer = request.match_info['peer']
        host, port = peer.split(':')
        await peers_collector.add_peer(host, port)
        return web.json_response({'message': 'ok'})

    app = web.Application(loop=loop)
    app.add_routes([web.get('/metrics', metrics),
                    web.get('/peers', peers),
                    web.get('/peers/add/{peer}', add_peer),
                    web.get('/hosts', hosts),
                    web.get('/ip', ip),
                    web.get('/prometheus{path:\w*}', prometheus),
                    web.get('/prometheus/{path:\w*}', prometheus)])

    return app

    # app = Flask(__name__)
    # app.json_encoder = JSONCustomEncoder
    # CORS(app)
    #
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.INFO)
    #
    # @app.route('/containers')
    # def containers():
    #     return jsonify(container_thread.containers_filtered)
    #
    # @app.route('/containers/all')
    # def containers_all():
    #     return jsonify(container_thread.get_all_containers())
    #

    # @app.route('/data')
    # def data():
    #     hash_length = 12
    #     nodes = container_thread.get_nodes(hash_length)
    #     edges = analyser_thread.get_edges()
    #     for p in peers_thread.other_peers:
    #         edges += get_edges_from_peer(p)
    #
    #     return jsonify({
    #         'nodes': nodes,
    #         'edges': edges
    #     })
    #
    # @app.route('/edges')
    # def get_edges():
    #     return jsonify(analyser_thread.get_edges())
    #
    # @app.route('/resolve_port/<port>')
    # def resolve_port(port):
    #     return jsonify(analyser_thread.resolve_port(port))
    #
    # @app.route('/ports')
    # def ports():
    #     return jsonify(analyser_thread.port_mapping)
    #
