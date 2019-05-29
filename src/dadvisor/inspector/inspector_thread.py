import subprocess
from threading import Thread

from dadvisor.config import FILTER_PORTS
from dadvisor.inspector.parser import parse_row
from dadvisor.log import log


class InspectorThread(Thread):
    """
    Reads data from the tcpdump program and store it in a queue, so that it can be processed further
    """

    def __init__(self, peers_collector, analyser):
        Thread.__init__(self, name='InspectorThread')
        self.peers_collector = peers_collector
        self.analyser = analyser

    def run(self):
        self.check_installation()
        args = [['not', 'port', str(port), 'and'] for port in FILTER_PORTS]
        args = [j for i in args for j in i]
        args.pop()  # remove last element (because it is 'and')

        p = subprocess.Popen(['tcpdump', '-i', 'any', '-n', '-l'] + args,
                             stdout=subprocess.PIPE)

        for row in iter(p.stdout.readline, b''):
            try:
                dataflow = parse_row(row.decode('utf-8'))
                if dataflow.size > 0 and not self.is_p2p_communication(dataflow):
                    self.analyser.loop.create_task(
                        self.analyser.analyse_dataflow(dataflow))
            except Exception as e:
                log.warn(e)
                log.warn('Cannot parse row: %s' % row.decode('utf-8').rstrip())

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            log.error('tcpdump is not installed. Please install it before running this code.\n')
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
