"""
This file contains all configurable options.
In the future, set these values based on environment variables.
"""

import os
import socket
import sys
from datetime import datetime

from dadvisor.log import log

# INTERNAL PORTS AND ADDRESSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
IP = os.environ.get('IP', socket.gethostbyname(socket.gethostname()))

PROXY_PORT = int(os.environ.get('DADVISOR_PORT', 14100))
INTERNAL_PORT = 14101
PROMETHEUS_PORT = 14102

CADVISOR_URL = 'http://localhost:14104'
PROMETHEUS_URL = 'http://localhost:{}/prometheus'.format(PROXY_PORT)
TRACKER = os.environ.get('TRACKER', 'http://35.204.250.252:14100')

FILTER_PORTS = os.environ.get('FILTER_PORTS', '22,{},{},{}'.
                              format(PROXY_PORT, INTERNAL_PORT, PROMETHEUS_PORT)).split(',')
log.info('Filtering internet traffic ports: {}'.format(FILTER_PORTS))


# INTERNET TRAFFIC
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
TRAFFIC_SAMPLE = int(os.environ.get('TRAFFIC_SAMPLE', 1000))
TRAFFIC_K = int(os.environ.get('TRAFFIC_K', 9))
TRAFFIC_SLEEP_MIN = int(os.environ.get('TRAFFIC_SLEEP_MIN', 1))
TRAFFIC_SLEEP_MAX = int(os.environ.get('TRAFFIC_SLEEP_MAX', 150))


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

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
log.setLevel(LOG_LEVEL)
# Possible log values: 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'


# DEFAULT FUNCTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
STARTED = datetime.now()


def seconds_up():
    return (datetime.now() - STARTED).seconds
