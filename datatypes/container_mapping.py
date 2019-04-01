class ContainerMapping(object):
    def __init__(self, host, container_ip, base_image, container_id):
        self.host = host
        self.container_ip = container_ip
        self.base_image = base_image
        self.id = container_id
        self.container_info = None

    def __dict__(self):
        return {'host': self.host, 'image': self.base_image, 'container': self.get_ip(), 'id': self.id}

    def __eq__(self, other):
        return self.host == other.host and \
               self.container_ip == other.container_ip and \
               self.id == other.id

    def __str__(self):
        return self.host + ':' + str(self.container_ip)

    def get_dict(self):
        return {'host': self.host,
                'image': self.base_image,
                'container': self.get_ip(),
                'id': self.id}

    def is_local(self):
        return self.container_ip.startswith('172')

    def get_ip(self):
        if not self.container_ip and self.container_info:
            return self.container_info.ip

    @staticmethod
    def decode(data, host, container_info):
        mapping = ContainerMapping(host, '', str(data['Image']), data['Id'])
        mapping.container_info = container_info
        return mapping
