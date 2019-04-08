from flask.json import JSONEncoder


class JSONCustomEncoder(JSONEncoder):

    def default(self, obj):
        from ..datatypes.address import Address
        from ..datatypes.container_info import ContainerInfo
        from ..datatypes.container_mapping import ContainerMapping
        from ..datatypes.dataflow import DataFlow
        from ..datatypes.peer import Peer
        if isinstance(obj, (Peer, Address, ContainerMapping, ContainerInfo, DataFlow)):
            return obj.__dict__()
        return JSONEncoder.default(self, obj)
