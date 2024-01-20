import flask

app = flask.Flask(__name__)

app.config.from_object('fablesite.config')
app.config.from_envvar('FABLESITE_SETTINGS', silent=True)

import fablesite.views
import fablesite.model
import fablesite.api

