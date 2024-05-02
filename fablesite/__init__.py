import flask
import os
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)
app.config.from_object("fablesite.config")
app.config.from_envvar("FABLESITE_SETTINGS", silent=True)
app.config["SECRET_KEY"] = os.urandom(24)

import fablesite.views
import fablesite.model
import fablesite.api
