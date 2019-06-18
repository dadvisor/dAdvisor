import json

from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from dadvisor.config import INTERNAL_PORT, PREFIX
from dadvisor.containers.cadvisor import get_machine_info
from dadvisor.datatypes.encoder import JSONCustomEncoder
from dadvisor.log import log


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', INTERNAL_PORT)
    log.info('Running on localhost:{}'.format(INTERNAL_PORT))
    await site.start()


async def get_app(loop, peers_collector, analyser, container_collector):
    """
    Expose a number of endpoints, such that nodes can communicate with each other.
    Note that every endpoint starts with PREFIX. This has been done, because all
    processes (dAdvisor, Prometheus, and Grafana) are reversed proxied to NGINX_PORT.
    Internally, they all have a different port, but now only one port needs to be opened
    on the host, to allow the communication.
    """
    num_cores, memory = await get_machine_info()

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

    async def ports(request):
        return web.json_response({**analyser.port_mapping, **analyser.ports})

    async def container_mapping(request):
        return web.json_response(container_collector.container_mapping)

    async def containers(request):
        return web.json_response(text=json.dumps(container_collector.containers_filtered,
                                                 cls=JSONCustomEncoder))

    async def get_info(request):
        return web.json_response(text=json.dumps({
            'num_cores': num_cores,
            'memory': memory,
        }))

    async def set_peers(request):
        data = await request.post()
        peers = data['nodes']
        await peers_collector.set_peers(peers)
        log.info(peers)
        return web.Response(body='OK')

    app = web.Application(loop=loop, debug=True, logger=log)
    app.add_routes([web.get('{}/metrics'.format(PREFIX), metrics),
                    web.get('{}/nodes'.format(PREFIX), peers),
                    web.get('{}/hosts'.format(PREFIX), hosts),
                    web.get('{}/ports'.format(PREFIX), ports),
                    web.get('{}/container_mapping'.format(PREFIX), container_mapping),
                    web.get('{}/containers'.format(PREFIX), containers),
                    web.get('{}/get_info'.format(PREFIX), get_info),
                    web.post('{}/set_peers'.format(PREFIX), set_peers)])
    return app
