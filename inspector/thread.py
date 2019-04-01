import subprocess
import sys
from queue import Queue
from threading import Thread

from inspector.parser import parse_row


class InspectorThread(Thread):

    def __init__(self, peers_thread):
        Thread.__init__(self)
        """
        A 2D dictionary, which is structured the following:
            self.data[src][dst] = size
            src and dst are an index in the addresses Database
        """
        self.data = Queue()
        self.peers_thread = peers_thread

    def run(self):
        self.check_installation()
        p = subprocess.Popen(('tcpdump', '-i', 'any', '-n', '-l'), stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            try:
                data_flow = parse_row(row.decode('utf-8'))
                if data_flow.size > 0 and \
                        int(data_flow.src.port) != 8800 and \
                        int(data_flow.dst.port) != 8800:
                    self.data.put(data_flow)
            except Exception:
                print('Cannot parse row: %s' % row.decode('utf-8'))

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            sys.stderr.write('tcpdump is not installed. Please install it before running this code.\n')
            sys.stderr.flush()
            exit(-1)
