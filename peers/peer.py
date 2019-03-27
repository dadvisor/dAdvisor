from peers.address import Address
from peers.database import Database


class Peer(object):

    def __init__(self, host, port):
        self.address = Address(host, port)
        self.can_be_removed = True

    def __dict__(self):
        return self.address.__dict__()

    def to_json(self):
        return self.address.to_json()

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __str__(self):
        return self.address.__str__()


if __name__ == '__main__':
    from flask import jsonify, Flask
    from web.encoder import JSONCustomEncoder

    app = Flask(__name__)
    app.json_encoder = JSONCustomEncoder


    @app.route('/')
    def home():
        d = Database(Peer('localhost', 5000))
        return jsonify(d)

    app.run(debug=True)
