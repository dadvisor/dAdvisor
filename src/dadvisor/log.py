"""
Declare some logging configuration, such that it prints pretty
"""

import logging

from dadvisor.config import LOG_LEVEL

log = logging.getLogger()
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
