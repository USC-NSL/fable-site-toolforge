"""Insta485 model (database) API."""

import pymysql
import flask
import fablesite


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if "db" not in flask.g:
        # host = fablesite.app.config['HOST']
        # username = fablesite.app.config['username']
        # password = fablesite.app.config['password']
        # db_name = fablesite.app.config['db_name']

        flask.g.db = pymysql.connect(
            host="",
            user="",
            password="",
            db="",
        )

    print(flask.g.db.cursor(pymysql.cursors.DictCursor))
    return flask.g.db.cursor(pymysql.cursors.DictCursor)


@fablesite.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    db = flask.g.pop("db", None)
    if db is not None:
        db.commit()
        db.close()
