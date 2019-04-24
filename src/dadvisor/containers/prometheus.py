import aiohttp

from dadvisor.config import PROMETHEUS_URL

URL = '{}/api/v1/query?query=sum(rate(container_cpu_usage_seconds_total[15s]))'.format(PROMETHEUS_URL)


async def get_cpu_stat():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            return await resp.json()
