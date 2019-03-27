from peers.address import Address


class Peer(object):

    def __init__(self, host, port):
        self.address = Address(host, port)
        self.can_be_removed = True

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __repr__(self):
        return self.address.__repr__()
