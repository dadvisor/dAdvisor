import json

import aiohttp

from dadvisor.config import TRACKER, PREFIX
from dadvisor.log import log


def _get_name(peer):
    return 'http://{}:{}{}'.format(peer.host, peer.port, PREFIX)


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Communication with nodes
# # # # # # # # # # # # # # # # # # # # # # # # #
async def get_node_info(node):
    return await _send_get(_get_name(node) + '/get_info')


async def get_ports(node):
    return await _send_get(_get_name(node) + '/ports')


async def get_container_mapping(node):
    return await _send_get(_get_name(node) + '/container_mapping')


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Communication with root
# # # # # # # # # # # # # # # # # # # # # # # # #
async def register_node(loop, node):
    log.info(f'Registering peer: {node}')
    loop.create_task(_send_post(f'{TRACKER}/root/add', data=node))


async def remove_node(loop, node):
    log.info(f'Removing peer: {node}')
    loop.create_task(_send_post(f'{TRACKER}/root/remove', data=node))


async def get_distribution():
    log.info('Get all nodes')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{TRACKER}/root/distribution') as resp:
            return resp.json()


async def _send_post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=json.dumps(data))
        return True
    except Exception as e:
        print(e)
    return False


async def _send_get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()
    except Exception as e:
        print(e)
        return None
