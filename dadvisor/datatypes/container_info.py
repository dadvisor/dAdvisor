import json
import subprocess
import time


class ContainerInfo(object):
    """
    Creates a ContainerInfo object with several properties.
    Note that the ip property is added later (in :func: validate), as Docker
    doesn't directly add an IP to the container.
    """

    def __init__(self, hash, load):
        self.hash = hash
        self.created = str(load['Created'])
        self.stopped = ''
        self.names = load['Names']
        self.image = str(load['Image'])
        self.ports = load['Ports']
        self.ip = ''

    def validate(self):
        if self.stopped:
            return
        for name in self.names:
            cmd = 'curl -s --unix-socket /var/run/docker.sock http://localhost/containers{}/json'.format(name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            data = json.loads(p.communicate()[0].decode('utf-8'))
            if 'message' in data:
                self.stopped = int(time.time())
                return
            elif 'NetworkSettings' in data:
                if data['NetworkSettings']['IPAddress']:
                    self.ip = data['NetworkSettings']['IPAddress']
                else:
                    networks = data['NetworkSettings']['Networks']
                    self.ip = next(iter(networks.values()))['IPAddress']

    def __dict__(self):
        return {
            'hash': self.hash,
            'created': self.created,
            'stopped': self.stopped,
            'names': self.names,
            'ports': self.ports,
            'image': self.image,
            'ip': self.ip
        }

    def to_container_mapping(self, host):
        from dadvisor.datatypes.container_mapping import ContainerMapping
        return ContainerMapping(host, self.ip, self.image, self.hash)
