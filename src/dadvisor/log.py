"""
Declare some logging configuration, such that it prints pretty
"""

import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
