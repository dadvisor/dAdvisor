"""
This file contains all configurable options.
In the future, set these values based on environment variables.
"""

import asyncio
import os
import socket
import sys
from datetime import datetime

import aiohttp

from dadvisor.log import log

PROXY_PORT = int(os.environ.get('NGINX_PORT', 14100))
INTERNAL_PORT = 14101
INTERNAL_IP = socket.gethostbyname(socket.gethostname())
CADVISOR_URL = 'http://localhost:14104'
PROMETHEUS_URL = 'http://localhost:{}/prometheus'.format(PROXY_PORT)

CACHE_TIME = 5


async def get_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org?format=json') as resp:
            data = await resp.json()
            return data['ip']


loop = asyncio.get_event_loop()
IP = loop.run_until_complete(get_ip())

DEFAULT_INFO_HASH = 'abc1234567890'
INFO_HASH = os.environ.get('INFO_HASH', DEFAULT_INFO_HASH)
if INFO_HASH == DEFAULT_INFO_HASH:
    log.error('Cannot use the default INFO_HASH. Run the program with the following command:')
    log.error('docker run --env INFO_HASH=... dadvisor/dadvisor')
    sys.exit(-1)

TRACKER = 'http://35.204.250.252:14100'
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
    return gb / 2 ** 30
