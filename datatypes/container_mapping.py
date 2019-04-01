class ContainerMapping(object):
    def __init__(self, host, container_ip, base_image, container_id):
        self.host = host
        self.container_ip = container_ip
        self.base_image = base_image
        self.id = container_id

    def __dict__(self):
        return {'host': self.host, 'image': self.base_image, 'container': self.container_ip, 'id': self.id}

    def __eq__(self, other):
        return self.host == other.host and \
               self.container_ip == other.container_ip and \
               self.id == other.id

    def __str__(self):
        return self.host + ':' + str(self.container_ip)

    def to_json(self):
        return {'host': self.host, 'image': self.base_image, 'container': self.container_ip, 'id': self.id}

    def is_local(self):
        return self.container_ip.startswith('172')

    @staticmethod
    def decode(data, containerInfo):
        mapping = ContainerMapping()
        return ContainerMapping(host,  '', str(data['Image']), data['Id'])
