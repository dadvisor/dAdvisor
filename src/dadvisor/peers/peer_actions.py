import os
import platform
import subprocess

import aiohttp

from dadvisor.config import TRACKER, INFO_HASH, PREFIX
from dadvisor.datatypes.peer import Peer
from dadvisor.log import log


def get_name(peer):
    return 'http://{}:{}{}'.format(peer.host, peer.port, PREFIX)


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT) == 0


async def fetch_peers(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/peers') as resp:
            return [Peer(p2['host'], p2['port']) for p2 in await resp.json()]


async def expose_peer(my_peer, other_peer):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                    get_name(other_peer) + '/peers/add/{}:{}'.format(my_peer.host, my_peer.port)) as resp:
                return await resp.json()
        except Exception as e:
            log.error(e)
            return []


async def get_containers(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/containers') as resp:
            return await resp.json()


async def get_container_ports(peer):
    async with aiohttp.ClientSession() as session:
        async with session.get(get_name(peer) + '/container_ports') as resp:
            return await resp.json()


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


async def remove_peer(peer):
    log.info('Removing peer: {}'.format(peer))
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/remove/{}/{}:{}'.format(TRACKER, INFO_HASH, peer.host, peer.port)) as resp:
            if resp.status == 200:
                return await resp.json()


async def get_tracker_info(peer):
    """ Get information about it's own node: parent and children """
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/node_info/{}/{}:{}'.format(TRACKER, INFO_HASH, peer.host, peer.port)) as resp:
            if resp.status == 200:
                data = await resp.json()
                log.info('Tracker info: {}'.format(data))
                return data
