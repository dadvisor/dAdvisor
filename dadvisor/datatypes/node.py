class Node(object):

    def __init__(self, ip: str, port: int, is_super_node: bool):
        self.ip = ip
        self.port = port
        self.is_super_node = is_super_node

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.ip == other.ip and \
                   self.port == other.port and \
                   self.is_super_node == other.is_super_node
        return False

    def __repr__(self):
        return f'Node({self.ip}, {self.port}, {self.is_super_node})'

    def to_json(self):
        return {'node': {
            'ip': self.ip,
            'port': self.port,
            'is_super_node': self.is_super_node
        }}
