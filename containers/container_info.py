import json

import requests


class ContainerInfo(object):

    def __init__(self, hash, load):
        self.hash = hash
        self.creation_time = str(load['creation_time'])
        self.aliases = [str(s) for s in load['aliases']]
        self.image = str(load['image'])
        self.ip = ''
        self.discover_ip()

    def discover_ip(self):
        for name in self.aliases:
            try:
                if not self.ip:
                    r = requests.get('http://localhost:5001/{}'.format(name))
                    array = json.loads(r.text)
                    print(array)
                    print('{}: {}'.format(name, array[0]))
                    self.ip = str(array[0])
            except Exception as e:
                print(e)
                continue
