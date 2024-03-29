"""Insta485 development configuration."""

import pathlib
import os

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = "/"

# Database file is var/fable.sqlite3
FABLE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATABASE_FILENAME = FABLE_ROOT / "var" / "fable.sqlite3"

HOST = os.environ.get("FABLE_DB_HOST", "")
USERNAME = os.environ.get("FABLE_DB_USERNAME", "")
PASSWORD = os.environ.get("FABLE_DB_PASSWORD", "")
DB_NAME = os.environ.get("FABLE_DB_NAME", "")

# HOST = "localhost"
# USERNAME = "root"
# PASSWORD = ""
# DB_NAME = "s55570__FABLE"
