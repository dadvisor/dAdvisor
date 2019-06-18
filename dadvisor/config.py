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
try:
    ip = socket.gethostbyname(socket.gethostname())
except socket.gaierror as e:
    log.error(e)
    ip = 'localhost'

IP = os.environ.get('IP', ip)

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


PREFIX = '/dadvisor'

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
log.setLevel(LOG_LEVEL)
# Possible log values: 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'


# DEFAULT FUNCTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
STARTED = datetime.now()


def seconds_up():
    return (datetime.now() - STARTED).seconds
