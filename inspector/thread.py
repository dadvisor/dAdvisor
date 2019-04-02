import subprocess
import sys
from queue import Queue
from threading import Thread

from inspector.parser import parse_row
from log import log


class InspectorThread(Thread):
    """
    Reads data from the tcpdump program and store it in a queue, so that it can be processed further
    """

    def __init__(self, peers_thread):
        Thread.__init__(self)
        self.data = Queue()
        self.peers_thread = peers_thread

    def run(self):
        self.check_installation()
        p = subprocess.Popen(('tcpdump', '-n', '-l'), stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            log.info(row.decode('utf-8').rstrip())
            try:
                data_flow = parse_row(row.decode('utf-8'))
                if data_flow.size > 0 and \
                        int(data_flow.src.port) != 8800 and \
                        int(data_flow.dst.port) != 8800:  # TODO update if condition
                    self.data.put(data_flow)
            except ValueError:
                log.warn('Cannot parse row: %s' % row.decode('utf-8').rstrip())

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            sys.stderr.write('tcpdump is not installed. Please install it before running this code.\n')
            sys.stderr.flush()
            exit(-1)
