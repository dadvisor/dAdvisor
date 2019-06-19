import json

import aiohttp

from dadvisor.config import TRACKER, PREFIX, CADVISOR_URL
from dadvisor.datatypes.encoder import JSONCustomEncoder
from dadvisor.log import log


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Communication with nodes
# # # # # # # # # # # # # # # # # # # # # # # # #
async def get_node_info(node):
    return await _send_get_json(_get_node_name(node) + '/get_info')


async def get_ports(node):
    return await _send_get_json(_get_node_name(node) + '/ports')


async def get_container_mapping(node):
    return await _send_get_json(_get_node_name(node) + '/container_mapping')


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Communication with root
# # # # # # # # # # # # # # # # # # # # # # # # #
def register_node(loop, node):
    log.info(f'Registering peer: {node}')
    loop.create_task(_send_post(f'{TRACKER}/root/add', data=node))


def remove_node(loop, node):
    log.info(f'Removing peer: {node}')
    loop.create_task(_send_post(f'{TRACKER}/root/remove', data=node))


async def get_all_nodes():
    return await _send_get_json(f'{TRACKER}/root/list')


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Communication with cAdvisor
# # # # # # # # # # # # # # # # # # # # # # # # #
async def get_machine_info():
    data = await _send_get_json(f'{CADVISOR_URL}/api/v2.0/machine')
    num_cores = data['num_cores']
    memory = sum([fs['capacity'] for fs in data['filesystems'] if fs['device'].startswith('/dev/')])
    return num_cores, memory


async def get_container_utilization():
    return await _send_get_json(f'{CADVISOR_URL}/api/v2.0/summary?type=docker&recursive=true')


# # # # # # # # # # # # # # # # # # # # # # # # #
#       Helper functions
# # # # # # # # # # # # # # # # # # # # # # # # #
def _get_node_name(node):
    return 'http://{}:{}{}'.format(node.ip, node.port, PREFIX)


async def _send_post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=json.dumps(data, cls=JSONCustomEncoder))
        return True
    except Exception as e:
        log.error(e)
        log.error(f'Cannot reach {url}')
    return False


async def _send_get(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()
    except Exception as e:
        log.error(e)
        log.error(f'Cannot reach {url}')
        return None


async def _send_get_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    except Exception as e:
        log.error(e)
        log.error(f'Cannot reach {url}')
        return None
