import aiohttp

from dadvisor.config import PROMETHEUS_URL
from dadvisor.log import log

URL = '{}/api/v1/query?query=sum(rate(container_cpu_usage_seconds_total[15s]))'.format(PROMETHEUS_URL)


async def get_cpu_stat():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            try:
                return await resp.json()
            except Exception as e:
                log.error(e)
                return resp
