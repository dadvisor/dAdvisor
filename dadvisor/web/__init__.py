import json

from aiohttp import web
from prometheus_client import generate_latest

from dadvisor.config import INTERNAL_PORT, PREFIX
from dadvisor.datatypes.node import Node
from dadvisor.log import log


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', INTERNAL_PORT)
    log.info('Running on localhost:{}'.format(INTERNAL_PORT))
    await site.start()


def get_app(loop, node_collector, analyser, container_collector):
    """
    Expose a number of endpoints, such that nodes can communicate with each other.
    Note that every endpoint starts with PREFIX. This has been done, because all
    processes (dAdvisor, Prometheus, and Grafana) are reversed proxied to NGINX_PORT.
    Internally, they all have a different port, but now only one port needs to be opened
    on the host, to allow the communication.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # #
    #       Communication with Prometheus
    # # # # # # # # # # # # # # # # # # # # # # # # #
    async def metrics(request):
        """ Each endpoint might use a request argument, but most of them don't need it."""
        return web.Response(body=generate_latest())

    # # # # # # # # # # # # # # # # # # # # # # # # #
    #       Communication with Peers
    # # # # # # # # # # # # # # # # # # # # # # # # #
    async def get_info(request):
        return web.json_response(text=json.dumps(node_collector.my_node_stats))

    async def mapping(request):
        return web.json_response(text=json.dumps({
            'ports': {**analyser.port_mapping, **analyser.ports},
            'containers': container_collector.container_mapping
        }))

    # # # # # # # # # # # # # # # # # # # # # # # # #
    #       Communication with root
    # # # # # # # # # # # # # # # # # # # # # # # # #
    async def set_distribution(request):
        data = json.loads(await request.json())
        nodes_json = data.get('nodes')
        nodes = []
        for node_json in nodes_json:
            node = node_json.get('node')
            nodes.append(Node(node.get('ip'), int(node.get('port')), node.get('is_super_node')))
        node_collector.set_scraper(nodes)
        return web.Response(body='OK')

    app = web.Application(loop=loop, debug=True, logger=log)
    app.add_routes([web.get(f'{PREFIX}/metrics', metrics),
                    web.get(f'{PREFIX}/get_info', get_info),
                    web.get(f'{PREFIX}/mapping', mapping),
                    web.post(f'{PREFIX}/set_distribution', set_distribution)])
    return app
