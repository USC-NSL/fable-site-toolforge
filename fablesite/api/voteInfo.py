import flask
import fablesite
import mwoauth
from flask import request, jsonify
from fablesite.api.link_algorithm.cli import process_urls, match_old_pattern, transform_url, clean_broken_link
from urllib.parse import urlparse
import re

@fablesite.app.route("/api/logout", methods=["GET"])
def logout():
    flask.session.clear()
    redirect = {"response": "success"}
    return flask.jsonify(redirect)


@fablesite.app.route("/api/login", methods=["GET"])
def login():
    """Display / route."""
    try:
        consumer_token = mwoauth.ConsumerToken(
            fablesite.app.config["CONSUMER_TOKEN"],
            fablesite.app.config["SECRET_TOKEN"],
        )
        redirect, request_token = mwoauth.initiate(
            "https://meta.wikimedia.org/w/index.php", consumer_token
        )
    except Exception:
        return flask.jsonify(error="OAuth initiation failed"), 500
    else:
        flask.session["request_token"] = dict(zip(request_token._fields, request_token))
        return flask.jsonify(url=redirect)


@fablesite.app.route("/api/oauth-callback")
def oauth_callback():
    """OAuth handshake callback."""
    if "request_token" not in flask.session:
        flask.flash("OAuth callback failed. Are cookies disabled?")
        return flask.redirect(flask.url_for("show_index"))

    consumer_token = mwoauth.ConsumerToken(
        fablesite.app.config["CONSUMER_TOKEN"],
        fablesite.app.config["SECRET_TOKEN"],
    )

    try:
        access_token = mwoauth.complete(
            "https://meta.wikimedia.org/w/index.php",
            consumer_token,
            mwoauth.RequestToken(**flask.session.pop("request_token")),
            flask.request.query_string,
        )

        identity = mwoauth.identify(
            "https://meta.wikimedia.org/w/index.php", consumer_token, access_token
        )
    except Exception:
        fablesite.app.logger.exception("OAuth authentication failed")
        return flask.redirect(
            flask.url_for("show_index")
        )  # Redirect to index with an error message
    else:
        flask.session["access_token"] = dict(zip(access_token._fields, access_token))
        flask.session["username"] = identity["username"]

    return flask.redirect(flask.url_for("show_index"))


@fablesite.app.route("/api/v1/get_all_aliases", methods=["GET"])
def all_aliases():
    """Display / route."""
    try:
        # Connect to database
        cur = fablesite.model.get_db()

        # Query database
        cur.execute("SELECT * FROM aliases where alias != link")

        aliasInfo = cur.fetchall()

        return flask.jsonify(aliasInfo)

    except Exception as e:
        print(e)
        flask.abort(500)


@fablesite.app.route("/api/v1/post_aliases/", methods=["POST"])
def post_aliases():
    """Display / route."""
    data = flask.request.get_json()

    try:
        for row in data:
            newRow = {
                "id": row["id"],
                "feedbackSelection": row["feedbackSelection"],
                "feedbackInput": row["feedbackInput"],
                "lastModifiedBy": row["username"],
            }

            updateFeedback(newRow)

        return flask.jsonify(success=True)

    except Exception as e:
        print(e)
        flask.abort(500)


def updateFeedback(data):
    id = data["id"]
    feedbackSelection = data["feedbackSelection"]
    feedbackInput = data["feedbackInput"]
    lastModifiedBy = data["lastModifiedBy"]

    cur = fablesite.model.get_db()

    cur.execute(
        """
        UPDATE aliases SET feedbackSelection = %s, feedbackInput = %s, lastModifiedBy = %s where id = %s
        """,
        [feedbackSelection, feedbackInput, lastModifiedBy, id],
    )


@fablesite.app.route("/api/get_search_alias/", methods=["GET"])
def get_search_alias():
    try:

        searchStr = request.args.get("search", default="", type=str)
        param = "%" + searchStr + "%"
        cur = fablesite.model.get_db()
        cur.execute("SELECT * FROM aliases where link like %s", [param])

        aliasInfo = cur.fetchall()
        return flask.jsonify(aliasInfo)

    except Exception as e:
        print(e)
        flask.abort(500)


# Not used
ACCURATE = "Correct"
CANT_TELL = "Unsure"
INACCURATE = "Incorrect"


# Not required
def addFeedback(data):
    id = data["id"]
    cur = fablesite.model.get_db()

    # cur.execute(
    #     """
    #     INSERT INTO idfeed (alias_id, user, description, accurate, inaccurate, mid) VALUES (%s, %s, %s, %s, %s, %s)
    #     """,
    #     [
    #         id,
    #         data["username"],
    #         data["description"],
    #         data[ACCURATE],
    #         data[INACCURATE],
    #         data[CANT_TELL],
    #     ],
    # )


# Not required
def updateValue(data, voteVal):
    id = data["id"]
    cur = fablesite.model.get_db()

    if voteVal == ACCURATE:
        cur.execute(
            "UPDATE feedback SET accurate = accurate + 1 WHERE alias_id = %s", [id]
        )
    elif voteVal == CANT_TELL:
        cur.execute("UPDATE feedback SET mid = mid + 1 WHERE alias_id = %s", [id])
    elif voteVal == INACCURATE:
        cur.execute(
            "UPDATE feedback SET inaccurate = inaccurate + 1 WHERE alias_id = %s", [id]
        )
    else:
        raise Exception("Invalid voteVal")


# Not required
@fablesite.app.route("/api/v1/get_alias/<id>", methods=["GET"])
def get_alias(id):
    """Display / route."""
    try:
        # Connect to database
        cur = fablesite.model.get_db()

        cur.execute(
            """
            SELECT aliases.*, feedback.accurate, feedback.inaccurate, feedback.mid
            FROM aliases
            LEFT JOIN feedback
            ON aliases.id = feedback.alias_id
            WHERE id = %s
            """,
            [id],
        )

        aliasInfo = cur.fetchone()

        return flask.jsonify(aliasInfo)

    except Exception as e:
        print(e)
        flask.abort(500)


# Not required
@fablesite.app.route("/api/v1/post_alias/<id>", methods=["POST"])
def post_alias(id):
    """Display / route."""
    data = flask.request.get_json()
    data["id"] = id
    data[ACCURATE] = int(data["quality"] == ACCURATE)
    data[CANT_TELL] = int(data["quality"] == CANT_TELL)
    data[INACCURATE] = int(data["quality"] == INACCURATE)

    try:
        addFeedback(data)
        updateValue(data, data["quality"])

        return flask.jsonify(success=True)
    except Exception as e:
        print(e)
        flask.abort(500)

@fablesite.app.route("/api/v1/autocomplete", methods=["POST"])
def autocomplete():
    data = flask.request.get_json()
    
    if not data or not isinstance(data, list):
        return flask.jsonify({'error': 'Invalid input format'}), 400

    training_data = [{'link': clean_broken_link(item['link']), 'alias': clean_broken_link(item['alias'])} 
                     for item in data[0]['training_links'] if item.get('feedbackSelection') == "Correct"]
    autocomplete_data = [{'link': clean_broken_link(item['link']), 'alias': clean_broken_link(item.get('alias', '')), "id": item['id']}
                         for item in data[0]['links_to_autocomplete'] if item.get('feedbackSelection') == "Unsure"]

    if len(training_data) < 2:
        return flask.jsonify({'error': 'Training data must contain at least 2 URL pairs'}), 400

    patterns = process_urls(training_data, False)
    
    results = []
    for item in autocomplete_data:
        domain = urlparse(item['link']).netloc
        
        if domain not in patterns:
            result = item.copy()
            result['feedbackSelection'] = "Unsure"
            results.append(result)
            continue
        
        pattern = patterns[domain]
        
        if isinstance(pattern, str):
            continue
        
        if match_old_pattern(item['link'], pattern['old_regex']):
            predicted_url = transform_url(item['link'], pattern['old_tokenized'], pattern['new_tokenized'])
            
            result = item.copy()

            if predicted_url.lower() == item['alias'].lower():
                result['feedbackSelection'] = "Correct"
            else:
                continue
        else:
            continue
        
        results.append(result)
    
    return flask.jsonify(results)