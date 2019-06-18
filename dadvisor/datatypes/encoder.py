from json import JSONEncoder


class JSONCustomEncoder(JSONEncoder):

    def default(self, obj):
        from dadvisor.datatypes.address import Address
        from dadvisor.datatypes.container_info import ContainerInfo
        from dadvisor.datatypes.dataflow import DataFlow
        from dadvisor.datatypes.node import Node
        if isinstance(obj, (Node, Address, ContainerInfo, DataFlow)):
            return obj.__dict__()
        return JSONEncoder.default(self, obj)
