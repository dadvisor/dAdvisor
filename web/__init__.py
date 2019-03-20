from flask import Flask, jsonify, render_template, request


def create_web_app(container_thread, inspector_thread):
    app = Flask(__name__)

    @app.route('/containers')
    def containers():
        if request.args.get('filtered', default=False, type=bool):
            c = container_thread.containers_filtered()
        else:
            c = container_thread.containers
        return jsonify({k: v.__dict__ for k, v, in c.items()})

    @app.route('/inspect/<src>')
    def inspect(src):
        return jsonify(inspector_thread.inspect(src))

    @app.route('/graph')
    def graph():
        return render_template('index.html')

    @app.route('/data')
    def data():
        hash_length = 12
        return jsonify({
            'nodes': container_thread.get_nodes(hash_length),
            'edges': inspector_thread.get_edges(container_thread, hash_length)
        })

    return app