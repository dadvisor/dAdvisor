class ContainerMapping(object):
    def __init__(self, host, container_ip, image, container_id):
        self.host = host
        self.container_ip = container_ip
        self.image = image
        self.id = container_id

    def __dict__(self):
        return {'host': self.host,
                'image': self.image,
                'container': self.container_ip,
                'id': self.id}

    def __eq__(self, other):
        return self.host == other.host and \
               self.container_ip == other.container_ip and \
               self.id == other.id

    def __str__(self):
        return self.host + ':' + str(self.container_ip)

    def get_dict(self):
        return {'host': self.host,
                'image': self.image,
                'container': self.container_ip,
                'id': self.id}
