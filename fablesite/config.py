"""Insta485 development configuration."""
import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Database file is var/fable.sqlite3
FABLE_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATABASE_FILENAME = FABLE_ROOT/'var'/'fable.sqlite3'