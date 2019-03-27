import json
import subprocess


class ContainerInfo(object):

    def __init__(self, hash, load):
        self.hash = hash
        self.created = str(load['Created'])
        self.aliases = [str(s) for s in load['Names']]
        self.image = str(load['Image'])
        self.__ip = ''

    @property
    def ip(self):
        if self.__ip:
            return self.__ip

        for name in self.aliases:
            try:
                cmd = 'curl --unix-socket /var/run/docker.sock http://localhost/containers/{}/json'.format(name)

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                data = json.loads(str(p.communicate()[0]))
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
            'aliases': self.aliases,
            'image': self.image,
            'ip': self.ip
        }
