class DataFlow(object):
    """
        stores the transmission of a certain amount of data from the source to the destination
    """

    def __init__(self, src, dst, size):
        self.src = src
        self.dst = dst
        self.size = size

    def __str__(self):
        return '{} > {}: {}'.format(self.src, self.dst, self.size)

    def __dict__(self):
        return {'src': self.src.__dict__(),
                'dst': self.dst.__dict__(),
                'size': self.size}
