import requests

from datatypes.peer import Peer
from log import log


def get_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://localhost:9050',
                       'https': 'socks5h://localhost:9050'}
    return session


def fetch_peers(peer):
    peer_list = get_session().get('http://{}:{}/peers'.format(peer.host, peer.port)).json()
    return [Peer(p2['host'], p2['port']) for p2 in peer_list]


def expose_peer(my_peer, other_peer):
    try:
        get_session().get(
            'http://{}:{}/peers/add/{}:{}'.format(other_peer.host, other_peer.port,
                                                  my_peer.host, my_peer.port)).json()
    except Exception as e:
        log.warn('Cannot send an address to {}'.format(other_peer))
        log.error(e)


def get_edges_from_peer(peer):
    return get_session().get('http://{}:{}/edges'.format(peer.host, peer.port)).json()


def get_ports(peer):
    return get_session().get('http://{}:{}/ports'.format(peer.host, peer.port)).json()


def get_containers(peer):
    return get_session().get('http://{}:{}/containers'.format(peer.host, peer.port)).json()
