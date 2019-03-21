class Peer(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
