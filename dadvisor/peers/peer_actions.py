import aiohttp

from dadvisor.config import TRACKER, PREFIX
from dadvisor.log import log


def get_name(peer):
    return 'http://{}:{}{}'.format(peer.host, peer.port, PREFIX)


async def get_peer_info(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/get_info') as resp:
            return await resp.json()


async def get_ports(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/ports') as resp:
            return await resp.json()


async def get_container_mapping(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/container_mapping') as resp:
            return await resp.json()


async def get_peer_list():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/peers'.format(TRACKER)) as resp:
            data = await resp.json()
            return data


async def register_peer(peer):
    log.info('Registering peer: {}'.format(peer))
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/add/{}:{}'.format(TRACKER, peer.host, peer.port)) as resp:
            if resp.status == 200:
                return await resp.json()


async def remove_peer(peer):
    log.info('Removing peer: {}'.format(peer))
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/remove/{}:{}'.format(TRACKER, peer.host, peer.port)) as resp:
            if resp.status == 200:
                return await resp.json()
