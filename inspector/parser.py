from peers.address import Address


def to_address(address):
    """
    Returns an Address-obj containing the host and the port
    Example input: 9d75df8be4c2.46622
    Example output: Address(9d75df8be4c2, 46622)
    """
    address = address.rstrip('.')  # remove last .
    array = address.split('.')
    return Address('.'.join(array[:-1]), array[-1])


def parse_size(s):
    """
    Converts a string to an integer
    Example input can either be: '(1234)' or '1234'
    Example output: 1234
    """
    s = s.replace('(', '').replace(')', '')
    return int(s)


def parse_row(row):
    row = row.rstrip()
    parts = row.split(' ')
    src = to_address(parts[2])
    dst = to_address(parts[4])

    try:
        size = parse_size(parts[-1])
    except ValueError:
        parts = row.split('length')[1]
        size = parse_size(parts.split(':')[0])
    return src, dst, size
