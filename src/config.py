import socket

import requests

PORT = 8800
INTERNAL_IP = socket.gethostbyname(socket.gethostname())
IP = requests.get('https://api.ipify.org?format=json').json()['ip']

MY_INFO_HASH = 'unique_token'.encode()

TRACKER_URI = 'udp://35.204.250.252:6969'