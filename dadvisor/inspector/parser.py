from dadvisor.datatypes.dataflow import DataFlow


def to_address(container_collector, address):
    """
    Returns an Address-obj containing the host, port, and possibly container
    """
    from ..datatypes.address import Address

    address = address.rstrip('.:')  # remove last . and :
    array = address.split('.')
    return Address.decode(container_collector,
                          '.'.join(array[:-1]), int(array[-1]))


def parse_size(s):
    """
    Converts a string to an integer
    Example input can either be: '(1234)' or '1234'
    Example output: 1234
    """
    s = s.replace('(', '').replace(')', '')
    return int(s)


def parse_row(container_collector, row):
    row = row.rstrip()
    parts = row.split(' ')
    src = to_address(container_collector, parts[1])
    dst = to_address(container_collector, parts[3])

    try:
        size = parse_size(parts[-1])
    except ValueError:
        parts = row.split('length')[1]
        size = parse_size(parts.split(':')[0])
    return DataFlow(src, dst, size)
