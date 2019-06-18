import aiohttp

from dadvisor.config import CADVISOR_URL


async def get_machine_info():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{CADVISOR_URL}/api/v2.0/machine') as resp:
            data = await resp.json()
            num_cores = data['num_cores']
            memory = sum([fs['capacity'] for fs in data['filesystems'] if fs['device'].startswith('/dev/')])
            return num_cores, memory


async def get_container_utilization():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{CADVISOR_URL}/api/v2.0/summary?type=docker&recursive=true') as resp:
            return await resp.json()
