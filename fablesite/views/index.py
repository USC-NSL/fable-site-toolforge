"""
Main Site View
"""
import flask
import fablesite

@fablesite.app.route('/', defaults={'path': ''})
@fablesite.app.route('/<path:path>')
def show_index(path):
    return flask.render_template("index.html")

