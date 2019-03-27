def remove_port(s):
    """
    Removes the last part of the string, which is the port.
    Example input: 9d75df8be4c2.46622
    Example output: 9d75df8be4c2
    """
    array = s.split('.')
    return '.'.join(array[:len(array) - 1])


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
    src = parts[2]
    dst = remove_port(parts[4])

    try:
        size = parse_size(parts[-1])
    except ValueError:
        parts = row.split('length')[1]
        size = parse_size(parts.split(':')[0])
    return src, dst, size
