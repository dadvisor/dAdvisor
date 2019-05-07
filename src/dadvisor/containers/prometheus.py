import aiohttp

from dadvisor.config import PROMETHEUS_URL
from dadvisor.log import log

URL = PROMETHEUS_URL + '/api/v1/query?query=rate(container_cpu_usage_seconds_total{id=~"/docker/.*",instance=~' \
                       '"localhost:.*"}[30s])/scalar(rate(container_cpu_usage_seconds_total{id="/"}[30s]))'


async def get_container_utilization():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            try:
                return await resp.json()
            except Exception as e:
                log.error(e)
                return resp
