"""
This file contains all configurable options.
In the future, set these values based on environment variables.
"""

import os
import socket
from datetime import datetime

from dadvisor.log import log

# INTERNAL PORTS AND ADDRESSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
try:
    ip = socket.gethostbyname(socket.gethostname())
except socket.gaierror as e:
    log.error(e)
    ip = 'localhost'

IP = os.environ.get('IP', ip)

IS_SUPER_NODE = os.environ.get('TYPE', 'NODE') == 'SUPERNODE'
PROXY_PORT = int(os.environ.get('DADVISOR_PORT', 14100))
INTERNAL_PORT = 14101
PROMETHEUS_PORT = 14102

CADVISOR_URL = 'http://localhost:14104'
PROMETHEUS_URL = f'http://localhost:{PROXY_PORT}/prometheus'
TRACKER = os.environ.get('TRACKER', 'http://35.204.250.252:14100')

FILTER_PORTS = os.environ.get('FILTER_PORTS',
                              f'22,{PROXY_PORT},{INTERNAL_PORT},{PROMETHEUS_PORT}').split(',')
log.info(f'Filtering internet traffic ports: {FILTER_PORTS}')

# INTERNET TRAFFIC
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
TRAFFIC_SAMPLE = int(os.environ.get('TRAFFIC_SAMPLE', 1000))
TRAFFIC_K = int(os.environ.get('TRAFFIC_K', 9))
TRAFFIC_SLEEP_MIN = int(os.environ.get('TRAFFIC_SLEEP_MIN', 1))
TRAFFIC_SLEEP_MAX = int(os.environ.get('TRAFFIC_SLEEP_MAX', 150))

SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 60))

PREFIX = '/dadvisor'

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
log.setLevel(LOG_LEVEL)
# Possible log values: 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'


# DEFAULT FUNCTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
STARTED = datetime.now()


def seconds_up():
    return (datetime.now() - STARTED).seconds
