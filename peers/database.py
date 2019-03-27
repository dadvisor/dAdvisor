class Database(object):
    def __init__(self, item=None):
        self.data = []
        if item:
            self.data.append(item)

    @property
    def length(self):
        return len(self.data)

    def exists(self, item):
        return item in self.data

    def get_id(self, item):
        return self.data.index(item)

    def add(self, item):
        self.data.append(item)

    def get(self, index):
        return self.data[index]

    def __repr__(self):
        return self.data

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.data

    def remove(self, item):
        self.data.remove(item)
