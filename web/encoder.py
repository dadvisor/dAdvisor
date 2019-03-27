from flask.json import JSONEncoder

from peers.database import Database


class JSONCustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Database):
            return obj.data
        try:
            return JSONEncoder.default(self, obj)
        except TypeError:
            return obj.__repr__
