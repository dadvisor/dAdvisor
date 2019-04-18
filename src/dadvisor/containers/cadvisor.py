import aiohttp

CADVISOR_URL = 'http://localhost:8080'


async def get_containers():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v2.0/stats/docker?recursive=true'.format(CADVISOR_URL)) as resp:
            return await resp.json()
