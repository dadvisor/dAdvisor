import subprocess
import time
from threading import Thread

from dadvisor.config import FILTER_PORTS, TRAFFIC_SAMPLE, TRAFFIC_SLEEP_TIME
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
        self.factor = 1

    def run(self):
        self.check_installation()
        args = [['not', 'port', str(port), 'and'] for port in FILTER_PORTS]
        args = [j for i in args for j in i]
        command = ['tcpdump', '-c', TRAFFIC_SAMPLE, '-i', 'any', '-nn', 'ip', 'and', '-l', '-t'] + args + \
                  ['tcp', 'and', '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)']
        log.info('Running command: {}'.format(' '.join(command)))

        while True:
            # start timer
            t = time.time()
            p = subprocess.Popen(command, stdout=subprocess.PIPE)

            # parse results
            for row in iter(p.stdout.readline, b''):
                try:
                    dataflow = parse_row(row.decode('utf-8'))
                    log.info(dataflow)
                    if dataflow.size > 0 and not self.is_p2p_communication(dataflow):
                        dataflow.size = round(dataflow.size * self.factor)
                        self.analyser.loop.create_task(self.analyser.analyse_dataflow(dataflow))
                except Exception as e:
                    log.warn(e)
                    log.warn('Cannot parse row: %s' % row.decode('utf-8').rstrip())

            elapsed = max(time.time() - t, 1)
            self.factor = max(TRAFFIC_SLEEP_TIME / elapsed, 1)
            time.sleep(TRAFFIC_SLEEP_TIME)
            log.debug('Set factor to: {}'.format(self.factor))

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            log.error('tcpdump is not installed. Please install it before running this code.')
            exit(-1)

    def is_p2p_communication(self, data_flow):
        """
        Skip communication between peers
        :return:
        """
        for p in self.peers_collector.peers:
            if (data_flow.src.host == p.address.host and int(data_flow.src.port) == int(p.address.port)) or \
                    (data_flow.dst.host == p.address.host and int(data_flow.dst.port) == int(p.address.port)):
                return True
        return False
