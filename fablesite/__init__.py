import flask
import os

app = flask.Flask(__name__)
app.config.from_object("fablesite.config")
app.config.from_envvar("FABLESITE_SETTINGS", silent=True)
app.config["SECRET_KEY"] = os.urandom(24)

import fablesite.views
import fablesite.model
import fablesite.api
