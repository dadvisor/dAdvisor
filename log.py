import logging

log = logging.getLogger()
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(module)s:%(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
