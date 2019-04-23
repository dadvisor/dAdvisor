import os
import socket

import requests

PROXY_PORT = int(os.environ.get('NGINX_PORT', 5000))
INTERNAL_PORT = 8800
INTERNAL_IP = socket.gethostbyname(socket.gethostname())
CADVISOR_URL = 'http://localhost:8080'
IP = requests.get('https://api.ipify.org?format=json').json()['ip']

INFO_HASH = os.environ.get('INFO_HASH', 'uniquetoken')

TRACKER = 'http://35.204.250.252:8080'
PREFIX = '/dadvisor'