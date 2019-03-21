class Peer(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.can_be_removed = True

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port
