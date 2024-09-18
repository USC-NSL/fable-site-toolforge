"""Insta485 development configuration."""

import pathlib
import os

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = "/"

# Database file is var/fable.sqlite3
FABLE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATABASE_FILENAME = FABLE_ROOT / "var" / "fable.sqlite3"

HOST = "localhost"
USERNAME = "root"
PASSWORD = "test123"
DB_NAME = "s55570__FABLE"
CONSUMER_TOKEN = "5acf42ce3c7496049897b6d5a717e3a4"
SECRET_TOKEN = "8ab88fee8b8347a23248ba276bc194326bd5a114"
