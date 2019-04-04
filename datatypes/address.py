import re


class Address(object):

    def __init__(self, host, container, port):
        self.host = host
        self.container = container
        self.port = port

    def __dict__(self):
        return {'host': self.host, 'container': self.container, 'port': self.port}

    def __eq__(self, other):
        return self.host == other.host and \
               str(self.port) == str(other.port) and \
               self.container == other.container

    def __str__(self):
        return '{}:{}:{}'.format(self.host, self.container, self.port)

    def is_local(self):
        return self.host == Address.IP and re.match(r'172.\d+.0.\d+', self.container)

    @staticmethod
    def is_host(host, container):
        return host == Address.IP and re.match(r'172.\d+.0.1', container)

    @staticmethod
    def decode(host_container, port):
        """
        :param host_container: either the address of a container, or of a host
        :param port:
        :return:
        """
        if re.match(r'172.\d+.0.\d+', host_container):
            return Address(Address.IP, host_container, port)
        return Address(host_container, '', port)

    @staticmethod
    @property
    def IP():
        return open("etc/tor/temp/hostname", "r").read().strip()
