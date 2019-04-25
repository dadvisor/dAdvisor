import os
import socket
from datetime import datetime

import aiohttp

PROXY_PORT = int(os.environ.get('NGINX_PORT', 5000))
INTERNAL_PORT = 8800
INTERNAL_IP = socket.gethostbyname(socket.gethostname())
CADVISOR_URL = 'http://localhost:8080'
PROMETHEUS_URL = 'http://localhost:{}/prometheus'.format(PROXY_PORT)


async def get_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org?format=json') as resp:
            data = await resp.json()
            return data['ip']


IP = await get_ip()

INFO_HASH = os.environ.get('INFO_HASH', 'uniquetoken')

TRACKER = 'http://35.204.250.252:8080'
PREFIX = '/dadvisor'

STARTED = datetime.now()

# Note currency is in USD
CPU_PRICE_HOUR = 0.021925
GB_PRICE_HOUR = 0.002938

CPU_PRICE_SECOND = CPU_PRICE_HOUR / 3600
GB_PRICE_SECOND = GB_PRICE_HOUR / 3600


def hours_up():
    return (datetime.now() - STARTED).seconds / 3600.0


def gb_to_bytes(gb):
    return gb / 2**30
