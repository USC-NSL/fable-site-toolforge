#!/bin/bash

# Stop on errors
# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -Eeuo pipefail


# setting flask variables
export FLASK_ENV=development
export FLASK_APP=fablesite

# running the dev server
flask run --host 0.0.0.0 --port 5000