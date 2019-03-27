import socket
import subprocess
import sys
from threading import Thread

from inspector.parser import parse_row

MAX_WIDTH = 10.0


class InspectorThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        """
        A 2D dictionary, which is structured the following:
            self.data[src][dst] = size
        """
        self.data = {}

    def run(self):
        self.check_installation()
        p = subprocess.Popen(('tcpdump', '-i', 'any', '-l'), stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            try:
                src, dst, size = parse_row(row.decode('utf-8'))
                if src.startswith('172'):
                    if src in self.data:
                        src_dict = self.data[src]
                        if dst in src_dict:
                            src_dict[dst] += size
                        else:
                            src_dict[dst] = size
                    else:
                        self.data[src] = {}
                        self.data[src][dst] = size

            except Exception:
                print('Cannot parse row: %s' % row.decode('utf-8'))

    def inspect(self, src):
        if src in self.data:
            return self.data[src]
        return []

    def get_edges(self, container_thread, hash_length):
        """
        :return: A list with a dict per data-flow of the containers
        """
        edges = []
        containers = container_thread.containers_filtered()
        ip_set = set([v.ip for v in containers.values()])
        for container_info in containers.values():
            src = container_info.ip
            if src in self.data:
                for dst in set(self.data[src].keys()) & ip_set:
                    edges.append({'data': {
                        'source': container_thread.get_hash_from_ip(src)[:hash_length],
                        'target': container_thread.get_hash_from_ip(dst)[:hash_length],
                        'bytes': self.data[src][dst]
                    }})
        return self.adjust_width(edges)

    def get_data(self):
        return {k: {self.lookup(k2): v2 for k2, v2 in v.items()} for k, v in self.data.items()}

    @staticmethod
    def lookup(name):
        """
        Returns the IP-address from a given name
        """
        ip_list = []
        try:
            ais = socket.getaddrinfo(name, 0, 0, 0, 0)
            for result in ais:
                ip_list.append(result[-1][0])
        except (socket.gaierror, UnicodeError) as e:
            print(e)

        return str(set(ip_list))

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            sys.stderr.write('tcpdump is not installed. Please install it before running this code.\n')
            sys.stderr.flush()
            exit(-1)

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
