import subprocess
import time
from threading import Thread

from dadvisor.config import FILTER_PORTS, TRAFFIC_SAMPLE, TRAFFIC_K, TRAFFIC_SLEEP_MAX, TRAFFIC_SLEEP_MIN
from dadvisor.inspector.parser import parse_row
from dadvisor.log import log


class InspectorThread(Thread):
    """
    Reads data from the tcpdump program and store it in a queue, so that it can be processed further
    """

    def __init__(self, node_collector, analyser):
        Thread.__init__(self, name='InspectorThread')
        self.node_collector = node_collector
        self.analyser = analyser
        self.running = True

    def run(self):
        self.check_installation()
        command = self.get_tcpdump_command()

        while self.running:
            """
            One iteration of this while loop performns the following actions:
            1. Run the tcpdump command that captures TRAFFIC_SAMPLE requests. 
                This is collected in X seconds.
            2. Resolve these requests by communicating with the other nodes
            3. Sleep k*X seconds, with a lower- and upperbound.
            """

            start_time = time.time()
            p = subprocess.Popen(command, stdout=subprocess.PIPE)

            # parse results
            for row in iter(p.stdout.readline, b''):
                try:
                    dataflow = parse_row(row.decode('utf-8'))
                    dataflow.size = dataflow.size * (TRAFFIC_K + 1)
                    self.analyser.loop.create_task(self.analyser.analyse_dataflow(dataflow))
                except Exception as e:
                    log.error(e)
                    log.error('Cannot parse row: {}'.format(row.decode('utf-8').rstrip()))

            end_time = time.time()
            elapsed = end_time - start_time
            log.info('Monitoring {} packets in {} sec'.format(TRAFFIC_SAMPLE, elapsed))

            self.analyser.loop.create_task(self.analyser.cache.resolve())

            # sleep K times the elapsed time. Minus the time it takes to resolve the cache
            sleep_time = TRAFFIC_K * elapsed - (time.time() - end_time)
            sleep_time = min(max(sleep_time, TRAFFIC_SLEEP_MIN), TRAFFIC_SLEEP_MAX)
            log.info('Sleeping for: {} sec'.format(sleep_time))
            time.sleep(sleep_time)

        log.info('Inspector thread stopped')

    @staticmethod
    def check_installation():
        try:
            subprocess.Popen(['tcpdump', '-D'], stdout=subprocess.PIPE)
        except ProcessLookupError:
            log.error('tcpdump is not installed. Please install it before running this code.')
            exit(-1)

    @staticmethod
    def get_tcpdump_command():
        args = [['not', 'port', str(port), 'and'] for port in FILTER_PORTS]
        args = [j for i in args for j in i]
        command = ['tcpdump', '-c', str(TRAFFIC_SAMPLE), '-i', 'any', '-nn', 'ip', 'and', '-l', '-t'] + args + \
                  ['tcp', 'and', '(((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)']
        log.info('Running command: {}'.format(' '.join(command)))
        return command

    def stop(self):
        log.info('Stopping InspectorThread')
        self.running = False
