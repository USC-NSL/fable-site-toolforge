import flask
import fablesite
import mwoauth
from flask import request, jsonify
from fablesite.api.link_algorithm import identify_pattern, apply_pattern, is_unpredictable, get_domain, generate_url_regex
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
    
    if not data or 'training_links' not in data or 'links_to_autocomplete' not in data:
        return flask.jsonify({'error': 'Invalid input format'}), 400
    
    training_data = [item for item in data if item.get('feedbackSelection') == "Correct"]
    autocomplete_data = [item for item in data if item.get('feedbackSelection') == "Unsure"]
    
    if len(training_data) < 2:
        return flask.jsonify({'error': 'Training data must contain at least 2 URL pairs'}), 400
    
    training_by_domain = {}
    for item in training_data:
        domain = get_domain(item['link'])
        if domain not in training_by_domain:
            training_by_domain[domain] = []
        training_by_domain[domain].append(item)
    
    for domain, items in training_by_domain.items():
        if len(items) < 2:
            return flask.jsonify({'error': f'Domain {domain} has less than 2 training pairs'}), 400
    
    autocomplete_by_domain = {}
    for item in autocomplete_data:
        domain = get_domain(item['link'])
        if domain not in autocomplete_by_domain:
            autocomplete_by_domain[domain] = []
        autocomplete_by_domain[domain].append(item)
    
    for domain in autocomplete_by_domain:
        if domain not in training_by_domain:
            return flask.jsonify({'error': f'No training data for domain {domain}'}), 400
    
    results = []
    for domain, items in autocomplete_by_domain.items():
        training_items = training_by_domain[domain]
        old_urls = [item['link'] for item in training_items]
        new_urls = [item['alias'] for item in training_items]
        
        if any(is_unpredictable(old, new) for old, new in zip(old_urls, new_urls)):
            return flask.jsonify({'error': f'Training data for domain {domain} contains unpredictable URLs'}), 400
        
        pattern = identify_pattern(old_urls, new_urls)
        
        training_regex = generate_url_regex(old_urls)
        
        for item in items:
            if re.match(training_regex, item['link']):
                predicted_url = apply_pattern(item['link'], pattern)
                
                if predicted_url.startswith('http://') and any(new_url.startswith('https://') for new_url in new_urls):
                    predicted_url = 'https://' + predicted_url[7:]
                
                result = item.copy()
                result['alias'] = predicted_url
                result['feedbackSelection'] = "Correct"
            else:
                result = item.copy()
                result['alias'] = item['link'] 
                result['feedbackSelection'] = "Unsure"
            
            results.append(result)
    
    return flask.jsonify(results)