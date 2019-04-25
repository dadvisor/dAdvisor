import aiohttp

from dadvisor.config import CADVISOR_URL


async def get_containers():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v2.0/stats/docker?recursive=true'.format(CADVISOR_URL)) as resp:
            return await resp.json()


async def get_machine_info():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v2.0/machine'.format(CADVISOR_URL)) as resp:
            return await resp.json()


async def get_storage_info():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v2.0/storage'.format(CADVISOR_URL)) as resp:
            return await resp.json()
