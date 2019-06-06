from typing import Dict, List

from dadvisor.datatypes.dataflow import DataFlow


class DataFlowCache(object):
    """
        implements a caching functionality, such that the
    """

    def __init__(self):
        self.data: Dict[str, List[DataFlow]] = {}
