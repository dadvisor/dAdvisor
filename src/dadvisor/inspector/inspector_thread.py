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
            """
            One iteration of this while loop performns the following actions:
            1. Run the tcpdump command that captures TRAFFIC_SAMPLE requests
            2. Resolve these requests by communicating with the other peers
            3. Sleep X seconds.
            
            The multiplication factor for the sampling is calculated as: 
               TRAFFIC_SLEEP_TIME over the time it takes to perform step 1.
               
            Step 2 and step 3 together consume TRAFFIC_SLEEP_TIME seconds.
            Therefore, the X from step 3 can be resolved as:
               TRAFFIC_SLEEP_TIME - time it takes to perform step 2.
            """

            start_time = time.time()
            p = subprocess.Popen(command, stdout=subprocess.PIPE)

            # parse results
            for row in iter(p.stdout.readline, b''):
                try:
                    dataflow = parse_row(row.decode('utf-8'))
                    if dataflow.size > 0 and not self.is_p2p_communication(dataflow):
                        dataflow.size = round(dataflow.size * self.factor)
                        self.analyser.loop.create_task(self.analyser.analyse_dataflow(dataflow))
                except Exception as e:
                    log.warn(e)
                    log.warn('Cannot parse row: %s' % row.decode('utf-8').rstrip())

            end_time = time.time()
            elapsed = max(end_time - start_time, 1)

            self.analyser.cache.resolve()

            self.factor = max(TRAFFIC_SLEEP_TIME / elapsed, 1)
            time.sleep(max(TRAFFIC_SLEEP_TIME - (time.time() - end_time), 0))
            log.info('Set factor to: {}'.format(self.factor))

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
