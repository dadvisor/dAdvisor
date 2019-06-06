import json

from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from dadvisor.config import INTERNAL_PORT, PREFIX
from dadvisor.datatypes.encoder import JSONCustomEncoder
from dadvisor.log import log
from dadvisor.peers.peer_actions import get_name


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', INTERNAL_PORT)
    log.info('Running on localhost:{}'.format(INTERNAL_PORT))
    await site.start()


def get_app(loop, peers_collector, analyser, container_collector):
    """
    Expose a number of endpoints, such that peers can communicate with each other.
    Note that every endpoint starts with PREFIX. This has been done, because all
    processes (dAdvisor, Prometheus, and Grafana) are reversed proxied to NGINX_PORT.
    Internally, they all have a different port, but now only one port needs to be opened
    on the host, to allow the communication.
    """

    async def metrics(request):
        """ Each endpoint might use a request argument, but most of them don't need it."""
        resp = web.Response(body=generate_latest())
        resp.content_type = CONTENT_TYPE_LATEST
        return resp

    async def hosts(request):
        return web.json_response(text=json.dumps(peers_collector.host_mapping,
                                                 cls=JSONCustomEncoder))

    async def peers(request):
        return web.json_response(text=json.dumps(peers_collector.peers,
                                                 cls=JSONCustomEncoder))

    async def add_peer(request):
        peer = request.match_info['peer']
        host, port = peer.split(':')
        await peers_collector.add_peer(host, port)
        return web.json_response({'message': 'ok'})

    async def dashboard(request):
        """
        All data is in the Prometheus of the root, so check if it has a parent. If it has,
        visit this endpoint of the parent. If not, redirect to /grafana.
        :param request:
        :return:
        """
        if peers_collector.parent:
            return web.HTTPFound(get_name(peers_collector.parent) + '/dashboard')
        else:
            return web.HTTPFound('/grafana')

    async def ports(request):
        return web.json_response(analyser.port_mapping)

    async def node_info(request):
        return web.json_response(text=json.dumps({'parent': peers_collector.parent,
                                                  'children': peers_collector.children},
                                                 cls=JSONCustomEncoder))

    async def containers(request):
        return web.json_response(text=json.dumps(container_collector.get_own_containers(),
                                                 cls=JSONCustomEncoder))

    app = web.Application(loop=loop, debug=True, logger=log)
    app.add_routes([web.get('{}/metrics'.format(PREFIX), metrics),
                    web.get('{}/peers'.format(PREFIX), peers),
                    web.get('{}/peers/add/'.format(PREFIX) + '{peer}', add_peer),
                    web.get('{}/hosts'.format(PREFIX), hosts),
                    web.get('{}/ports'.format(PREFIX), ports),
                    web.get('{}/dashboard'.format(PREFIX), dashboard),
                    web.get('{}/node_info'.format(PREFIX), node_info),
                    web.get('{}/containers'.format(PREFIX), containers)])
    return app
