import asyncio
import random
import struct
from datetime import timedelta, datetime
from ipaddress import ip_address


class UdpTrackerClientProto(asyncio.Protocol):
    def __init__(self, client):
        self.client = client
        self.received_msg = None
        self.transport = None
        self.sent_msgs = {}
        self.logger = self.client.logger
        self.connection_lost_received = asyncio.Event()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.connection_lost_received.set()

    def datagram_received(self, data, addr):
        if len(data) < 8:
            self.logger.warning('Invalid datagram received.')
            return

        action, tid = struct.unpack('!II', data[:8])
        if tid in self.sent_msgs:
            self.received_msg = (action, tid, data[8:])
            self.sent_msgs[tid].set()
        else:
            self.logger.warning('Invalid transaction ID received.')

    def error_received(self, exc):
        self.logger.info('UDP client transmision error: {}'.format(exc))

    def get_tid(self):
        tid = random.randint(0, 0xffffffff)
        while tid in self.sent_msgs:
            tid = random.randint(0, 0xffffffff)
        self.sent_msgs[tid] = asyncio.Event()
        return tid

    async def send_msg(self, msg, tid):
        n = 0
        timeout = 15

        for i in range(self.client.max_retransmissions):
            try:
                self.transport.sendto(msg)
                await asyncio.wait_for(self.sent_msgs[tid].wait(), timeout=timeout)

                del self.sent_msgs[tid]
            except asyncio.TimeoutError:
                if n >= self.client.max_retransmissions - 1:
                    del self.sent_msgs[tid]
                    raise TimeoutError('Tracker server timeout.')

                action = int.from_bytes(msg[8:12], byteorder='big')
                if action != 0:  # if not CONNECT
                    delta = timedelta(seconds=self.client.connid_valid_period)
                    if self.client.connid_timestamp < datetime.now() - delta:
                        await self.connect()

                n += 1
                timeout = 15 * 2 ** n

                self.logger.info(
                    'Request timeout. Retransmitting. '
                    '(try #{}, next timeout {} seconds)'.format(n, timeout))
            else:
                return

    async def connect(self):
        self.logger.info('Sending connect message.')
        tid = self.get_tid()
        msg = struct.pack('!QII', 0x41727101980, 0, tid)
        await self.send_msg(msg, tid)
        if self.received_msg:
            action, tid, data = self.received_msg
            self.client.callback('connected')
            self.client.connid = int.from_bytes(data, byteorder='big')
            self.client.connid_timestamp = datetime.now()

            self.received_msg = None
        else:
            self.logger.info('No reply received.')

    async def announce(self, infohash, event, num_want=20):
        if not self.client.interval or not self.client.connid or \
                datetime.now() > self.client.connid_timestamp + \
                timedelta(seconds=self.client.connid_valid_period):
            # get a connection id first
            await self.connect()

            if not self.client.connid:
                self.logger.info('No reply to connect message.')
                return

        self.logger.info('Sending announce message.')
        action = 1
        tid = self.get_tid()
        ip, port = self.client.address
        key = random.randint(0, 0xffffffff)
        ip = int.from_bytes(ip_address(ip).packed, byteorder='big')
        msg = struct.pack('!QII20s20sIIIIH', self.client.connid, action, tid,
                          infohash, self.client.peerid, event, ip, key, num_want, port)
        await self.send_msg(msg, tid)
        if self.received_msg:
            action, tid, data = self.received_msg
            self.received_msg = None

            if len(data) % 6 != 0:
                self.logger.warning(
                    'Invalid announce reply received. Invalid length.')
                return None

            peers = [data[i:i + 6] for i in range(0, len(data), 6)]
            peers = [(str(ip_address(p[:4])), int.from_bytes(p[4:], byteorder='big'))
                     for p in peers]

            self.client.callback('announced', infohash, peers)
        else:
            peers = None
            self.logger.info('No reply received to announce message.')

        return peers
