from threading import Thread

MAX_WIDTH = 10.0


class AnalyserThread(Thread):

    def __init__(self, inspector_thread, container_thread):
        Thread.__init__(self)
        self.running = True
        self.inspector_thread = inspector_thread
        self.container_thread = container_thread
        self.data = {}  # 2D dict, that can be used as: self.data[src][dst] = data size

    def run(self):
        while self.running:
            dataflow = self.inspector_thread.data.get()
            src_id = self.address_id(dataflow.src)
            dst_id = self.address_id(dataflow.dst)
            if src_id == -1 or dst_id == -1:
                print('Skipping: {}'.format(dataflow))
                continue
            if src_id in self.data:
                if dst_id in self.data[src_id]:
                    self.data[src_id][dst_id] += dataflow.size
                else:
                    self.data[src_id][dst_id] = dataflow.size
            else:
                self.data[src_id][dst_id] = dataflow.size


    def address_id(self, address):
        """
        Get the local address from a given host (assuming that this host is a peer)
        :param address:
        :return:
        """
        for index, item in enumerate(self.container_thread.get_all_containers()):
            if address.host == item.host and address.container == item.container_ip:
                return index
        return -1

    @staticmethod
    def adjust_width(edges):
        try:
            max_width = max([edge['data']['bytes'] for edge in edges])
            scale = MAX_WIDTH / max_width
        except ValueError:
            scale = 1
        for edge in edges:
            edge['data']['width'] = edge['data']['bytes'] * scale
        return edges
