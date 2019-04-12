from .tracker_client import TrackerClient


async def announce(address):
    client = TrackerClient(announce_uri='udp://35.204.250.252:6969', address=address)
    await client.start()
    peers = await client.start_announce(b'myhash')
    client.logger.info('Peers: {}'.format(peers))
    return peers
