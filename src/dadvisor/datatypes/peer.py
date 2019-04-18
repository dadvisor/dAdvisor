from dadvisor.datatypes.address import Address


class Peer(object):

    def __init__(self, host, port):
        self.address = Address(host, '', port)

    @property
    def host(self):
        return self.address.host

    @property
    def port(self):
        return self.address.port

    def __dict__(self):
        return self.address.__dict__()

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __str__(self):
        return self.address.__str__()
