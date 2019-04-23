import json

import aiohttp
from aiohttp import web
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from dadvisor.config import INTERNAL_IP, IP, INTERNAL_PORT, PREFIX
from dadvisor.datatypes.encoder import JSONCustomEncoder
from dadvisor.log import log


async def run_app(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', INTERNAL_PORT)
    log.info('Running on localhost:{}'.format(INTERNAL_PORT))
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
            async with session.request(request.method, 'http://localhost:9090{}'.format(path)) as resp:
                # resp.
                response = web.StreamResponse(status=resp.status, reason='OK', headers=request.headers)
                await response.prepare(request)
                while True:
                    chunk = await resp.content.read()
                    if not chunk:
                        break
                    await response.write(chunk)
                return response
        # return web.Response(body=raw, status=resp.status, headers=resp.headers)

    async def add_peer(request):
        peer = request.match_info['peer']
        host, port = peer.split(':')
        await peers_collector.add_peer(host, port)
        return web.json_response({'message': 'ok'})

    app = web.Application(loop=loop, debug=True, logger=log)
    app.add_routes([web.get('{}/metrics'.format(PREFIX), metrics),
                    web.get('{}/peers'.format(PREFIX), peers),
                    web.get('{}/peers/add/'.format(PREFIX) + '{peer}', add_peer),
                    web.get('{}/hosts'.format(PREFIX), hosts),
                    web.get('{}/ip'.format(PREFIX), ip)])
    # app.router.add_route('*', '/prometheus{path:.*?}', prometheus)

    return app
