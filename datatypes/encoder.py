from flask.json import JSONEncoder

from datatypes.address import Address
from datatypes.container_info import ContainerInfo
from datatypes.container_mapping import ContainerMapping
from datatypes.peer import Peer


class JSONCustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Peer, Address, ContainerMapping, ContainerInfo)):
            return obj.to_json()
        return JSONEncoder.default(self, obj)
