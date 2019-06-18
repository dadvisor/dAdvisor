import aiohttp

from dadvisor.config import CADVISOR_URL


async def get_machine_info():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v2.0/machine'.format(CADVISOR_URL)) as resp:
            data = await resp.json()
            num_cores = data['num_cores']
            memory = sum([fs['capacity'] for fs in data['filesystems'] if fs['device'].startswith('/dev/')])
            return num_cores, memory
