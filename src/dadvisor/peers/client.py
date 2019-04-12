from dadvisor.config import TRACKER_URI, MY_INFO_HASH
from dadvisor.peers.tracker_client import TrackerClient


async def announce(address):
    client = TrackerClient(announce_uri=TRACKER_URI, address=address)
    await client.start()
    peers = await client.start_announce(MY_INFO_HASH)
    client.logger.info('Peers: {}'.format(peers))
    return peers
