from flask.json import JSONEncoder

from peers.address import Address
from peers.database import Database
from peers.peer import Peer


class JSONCustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Database, Peer, Address)):
            return obj.to_json()
        return JSONEncoder.default(self, obj)
