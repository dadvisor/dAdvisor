import requests

from dadvisor.config import INTERNAL_IP, IP
from dadvisor.datatypes.peer import Peer
from dadvisor.log import log


def fetch_peers(peer):
    peer_list = requests.get('http://{}:{}/peers'.format(peer.host, peer.port)).json()
    return [Peer(p2['host'], p2['port']) for p2 in peer_list]


def expose_peer(my_peer, other_peer):
    try:
        requests.get(
            'http://{}:{}/peers/add/{}:{}'.format(other_peer.host, other_peer.port,
                                                  my_peer.host, my_peer.port)).json()
    except Exception as e:
        log.warn('Cannot send an address to {}'.format(other_peer))
        log.error(e)


def get_edges_from_peer(peer):
    return requests.get('http://{}:{}/edges'.format(peer.host, peer.port)).json()


def get_ports(peer):
    return requests.get('http://{}:{}/ports'.format(peer.host, peer.port)).json()


def get_containers(peer):
    return requests.get('http://{}:{}/containers'.format(peer.host, peer.port)).json()


def get_ip(peer):
    try:
        data = requests.get('http://{}:{}/ip'.format(peer.host, peer.port)).json()
        return data['internal'], data['external']
    except Exception as e:
        log.error(e)
        return INTERNAL_IP, IP
