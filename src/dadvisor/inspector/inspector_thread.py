import subprocess
import sys
from threading import Thread

from dadvisor.config import PORT
from dadvisor.inspector.parser import parse_row
from dadvisor.log import log


class InspectorThread(Thread):
    """
    Reads data from the tcpdump program and store it in a queue, so that it can be processed further
    """

    def __init__(self, peers_collector):
        Thread.__init__(self, name='InspectorThread')
        self.data = None
        self.peers_collector = peers_collector

    def run(self):
        self.check_installation()
        p = subprocess.Popen(('tcpdump', '-i', 'any', '-n', '-l', 'not', 'port', '22', 'and', 'not', 'port', str(PORT)),
                             stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            try:
                data_flow = parse_row(row.decode('utf-8'))
                if data_flow.size > 0 and not self.is_p2p_communication(data_flow):
                    if self.data:
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

    def is_p2p_communication(self, data_flow):
        """
        Skip communication between peers
        :return:
        """
        for p in self.peers_collector.peers:
            if (data_flow.src.host == p.address.host and str(data_flow.src.port) == str(p.address.port)) or \
                    (data_flow.dst.host == p.address.host and str(data_flow.dst.port) == str(p.address.port)):
                return True
        return False
