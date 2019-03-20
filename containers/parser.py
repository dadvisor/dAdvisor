def parse_hash(key):
    """
    Parses the hash of a name.
    :param key: For example: '/docker/895ad81a36dee14c8303938f1add74c80800f2d15521c1be48b8db4cc3dcbd23'
    :return: the last part: i.e. : '895ad81a36dee14c8303938f1add74c80800f2d15521c1be48b8db4cc3dcbd23'
    """
    return key.split('/')[-1]
