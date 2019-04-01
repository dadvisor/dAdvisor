import subprocess
import sys
from threading import Thread

from inspector.parser import parse_row
from datatypes.database import Database

MAX_WIDTH = 10.0


class InspectorThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        """
        A 2D dictionary, which is structured the following:
            self.data[src][dst] = size
            src and dst are an index in the addresses Database
        """
        self.data = {}
        self.addresses = Database()

    def run(self):
        self.check_installation()
        p = subprocess.Popen(('tcpdump', '-i', 'any', '-n', '-l'), stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            try:
                src, dst, size = parse_row(row.decode('utf-8'))
                if src.is_local() or dst.is_local():
                    src_id = self.addresses.get_id(src)
                    dst_id = self.addresses.get_id(dst)
                    if src_id in self.data:
                        src_dict = self.data[src_id]

                        if dst_id in src_dict:
                            src_dict[dst_id] += size
                        else:
                            src_dict[dst_id] = size
                    else:
                        self.data[src_id] = {}
                        self.data[src_id][dst_id] = size
            except Exception:
                print('Cannot parse row: %s' % row.decode('utf-8'))

    def map(self, container_thread, port):
        ip_set = set()

        for container, data in list(container_thread.containers_filtered.items()):
            for port_obj in data.ports:
                if str(port_obj['PublicPort']) == port:
                    ip_set.add(data.ip)

        for src_id, v in list(self.data.items()):
            src = self.addresses.get(src_id)
            if src.port == port:
                ip_set.add(src.host)
            for dst_id in list(v.keys()):
                dst = self.addresses.get(dst_id)
                if dst.port == port:
                    ip_set.add(dst.host)
        return list(ip_set)

    def get_data_for_host(self, host):
        addresses = Database()
        data = {}
        for src_old_id, dst_dict in list(self.data.items()):
            src = self.addresses.get(src_old_id)
            if src.host == host:
                src_new_id = addresses.get_id(src)
                if src_new_id not in data:
                    data[src_new_id] = {}
                for dst_old_id in dst_dict.keys():
                    dst_new_id = addresses.get_id(self.addresses.get(dst_old_id))
                    data[src_new_id][dst_new_id] = self.data[src_old_id][dst_old_id]
            else:
                for dst_old_id in dst_dict.keys():
                    if self.addresses.get(dst_old_id).host == host:
                        src_new_id = addresses.get_id(src)
                        if src_new_id not in data:
                            data[src_new_id] = {}
                        dst_new_id = addresses.get_id(self.addresses.get(dst_old_id))
                        data[src_new_id][dst_new_id] = self.data[src_old_id][dst_old_id]

        return {'data': data, 'addresses': addresses}

    def get_edges(self, container_thread, hash_length):
        """
        :return: A list with a dict per data-flow of the containers
        """
        edges = []
        containers = container_thread.containers_filtered
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
        return {'data': self.data,
                'addresses': self.addresses}

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
