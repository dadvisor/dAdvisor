import random

from prometheus_client import start_http_server, Counter

if __name__ == '__main__':
    start_http_server(8000)
    c = Counter('test', 'description')
    while True:
        c.inc(random.random())
