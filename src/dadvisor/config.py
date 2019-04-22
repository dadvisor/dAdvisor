import os
import socket

import requests

PORT = int(os.environ.get('PORT', 8800))
INTERNAL_IP = socket.gethostbyname(socket.gethostname())
IP = requests.get('https://api.ipify.org?format=json').json()['ip']

INFO_HASH = 'uniquetoken'

TRACKER = 'http://35.204.250.252:8080'
PREFIX = '/dadvisor'