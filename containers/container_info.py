import json
import subprocess


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
                cmd = "curl --unix-socket /var/run/docker.sock http://localhost/containers/{}/json".format(name)

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                data = json.loads(p.communicate()[0])
                print(data)
                return str(data['NetworkSettings']['IPAddress'])
            except Exception as e:
                print(e)
                continue
        return ''
