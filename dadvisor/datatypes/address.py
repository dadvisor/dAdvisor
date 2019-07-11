import re

from dadvisor.config import IP


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
        if not self.container:
            return '{}:{}'.format(self.host, self.port)
        else:
            return '{}:{}:{}'.format(self.host, self.container, self.port)

    def __hash__(self):
        return hash(str(self))

    def is_local(self):
        return self.host == IP

    @staticmethod
    def decode(container_collector, host_container, port):
        """
        :param host_container: either the address of a container, or of a host
        :param port:
        :return:
        """
        if host_container in container_collector.container_mapping.keys():
            return Address(IP, host_container, port)
        return Address(host_container, '', port)
