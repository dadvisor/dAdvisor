from flask.json import JSONEncoder

from dadvisor.datatypes.address import Address
from dadvisor.datatypes.container_info import ContainerInfo
from dadvisor.datatypes.container_mapping import ContainerMapping
from dadvisor.datatypes.dataflow import DataFlow
from dadvisor.datatypes.peer import Peer


class JSONCustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Peer, Address, ContainerMapping, ContainerInfo, DataFlow)):
            return obj.__dict__()
        return JSONEncoder.default(self, obj)
