from flask.json import JSONEncoder

from datatypes.address import Address
from datatypes.database import Database
from datatypes.peer import Peer


class JSONCustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Database, Peer, Address)):
            return obj.to_json()
        return JSONEncoder.default(self, obj)
