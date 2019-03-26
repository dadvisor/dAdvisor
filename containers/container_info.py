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
                p = subprocess.Popen(('docker', 'ps', '', '-q', '|', 'xargs', '-n', '1', 'docker', 'inspect',
                                      "--format '{{ .NetworkSettings.IPAddress }} {{ .Name }}'", '|', 'grep', name),
                                     stdout=subprocess.PIPE)
                return p.communicate()[0]
            except Exception as e:
                print(e)
                continue
        return ''
