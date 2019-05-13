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

# INTERNAL PORTS AND ADDRESSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
PROXY_PORT = int(os.environ.get('NGINX_PORT', 14100))
INTERNAL_PORT = 14101

CADVISOR_URL = 'http://localhost:14104'
PROMETHEUS_URL = 'http://localhost:{}/prometheus'.format(PROXY_PORT)
TRACKER = 'http://35.204.250.252:14100'

CACHE_TIME = 5


# IP ADDRESSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
async def get_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org?format=json') as resp:
            data = await resp.json()
            return data['ip']


INTERNAL_IP = socket.gethostbyname(socket.gethostname())
loop = asyncio.get_event_loop()
IP = loop.run_until_complete(get_ip())
log.info('IP: {}'.format(IP))

# INFO_HASH
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
DEFAULT_INFO_HASH = 'abc1234567890'
INFO_HASH = os.environ.get('INFO_HASH', DEFAULT_INFO_HASH)
if INFO_HASH == DEFAULT_INFO_HASH:
    log.error('Cannot use the default INFO_HASH. Run the program with the following command:')
    log.error('docker run --env INFO_HASH=... dadvisor/dadvisor')
    sys.exit(-1)

log.info('INFO_HASH: {}'.format(INFO_HASH))
PREFIX = '/dadvisor'

# PRICE CONFIGURATION
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
CPU_PRICE_HOUR = 0.021925  # Currency is in USD
GB_PRICE_HOUR = 0.002938


def get_price_per_hour(num_cpu, num_gb):
    return num_cpu * CPU_PRICE_HOUR + num_gb * GB_PRICE_HOUR


# DEFAULT FUNCTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
STARTED = datetime.now()


def seconds_up():
    return (datetime.now() - STARTED).seconds
