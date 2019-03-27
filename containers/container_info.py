import json
import subprocess


class ContainerInfo(object):

    def __init__(self, hash, load):
        self.hash = hash
        self.created = str(load['Created'])
        self.names = load['Names'].decode('utf-8')
        self.image = str(load['Image'])
        self.ports = str(load['Ports'])
        self.__ip = ''

    @property
    def ip(self):
        if self.__ip:
            return self.__ip

        for name in self.names:
            try:
                cmd = 'curl --unix-socket /var/run/docker.sock http://localhost/containers/{}/json'.format(name)

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                data = json.loads(p.communicate()[0])
                print(data)
                self.__ip = str(data['NetworkSettings']['IPAddress'])
                return self.__ip
            except Exception as e:
                print(e)
                continue
        return self.__ip

    def get_dict(self):
        return {
            'hash': self.hash,
            'creation_time': self.created,
            'names': self.names,
            'ports': self.ports,
            'image': self.image,
            'ip': self.ip
        }
