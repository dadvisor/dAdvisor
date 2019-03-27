class Address(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __dict__(self):
        return {'host': self.host, 'port': self.port}

    def __eq__(self, other):
        return self.host == other.host and str(self.port) == str(other.port)

    def __str__(self):
        return self.host + ':' + str(self.port)

    def to_json(self):
        return {'host': self.host, 'port': self.port}
