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
        if item in self.data:
            return self.data.index(item)
        self.add(item)
        return len(self.data) - 1

    def add(self, item):
        self.data.append(item)

    def get(self, index):
        return self.data[index]

    def __len__(self):
        return self.length

    def to_list(self):
        return self.data

    def __iter__(self):
        return iter(self.data)

    def to_json(self):
        return [item.to_json() for item in self.data]

    def remove(self, item):
        self.data.remove(item)
