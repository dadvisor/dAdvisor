import logging

log = logging.getLogger()
log.setLevel(logging.INFO)
console = logging.StreamHandler()
format_str = '%(asctime)s\t%(levelname)s -- %(thread)d:%(filename)s:%(lineno)s -- %(message)s'
console.setFormatter(logging.Formatter(format_str))
log.addHandler(console)
