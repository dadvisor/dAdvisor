import aiohttp
import requests

from dadvisor.config import TRACKER, INFO_HASH
from dadvisor.datatypes.peer import Peer
from dadvisor.log import log


async def fetch_peers(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://{}:{}/peers'.format(peer.host, peer.port)) as resp:
            return [Peer(p2['host'], p2['port']) for p2 in await resp.json()]


async def expose_peer(my_peer, other_peer):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                    'http://{}:{}/peers/add/{}:{}'.format(other_peer.host, other_peer.port,
                                                          my_peer.host, my_peer.port)) as resp:
                return await resp.json()
        except Exception as e:
            log.error(e)
            return ''


def get_edges_from_peer(peer):
    return requests.get('http://{}:{}/edges'.format(peer.host, peer.port)).json()


async def get_ports(peer):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://{}:{}/ports'.format(peer.host, peer.port)) as resp:
                return resp.json()
        except Exception as e:
            log.error(e)
            return ''

def get_containers(peer):
    return requests.get('http://{}:{}/containers'.format(peer.host, peer.port)).json()


async def get_ip(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://{}:{}/ip'.format(peer.host, peer.port)) as resp:
            data = await resp.json()
            return data['internal'], data['external']


async def get_peer_list():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/peers/{}'.format(TRACKER, INFO_HASH)) as resp:
            data = await resp.json()
            return data


async def register_peer(peer):
    log.info('Registering peer: {}'.format(peer))
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/add/{}/{}:{}'.format(TRACKER, INFO_HASH, peer.host, peer.port)) as resp:
            if resp.status == 200:
                return await resp.json()