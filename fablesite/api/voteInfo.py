import flask
import fablesite

ACCURATE = "Correct"
CANT_TELL = "Unsure"
INACCURATE = "Incorrect"

def addFeedback(data):
    id = data["id"]
    cur = fablesite.model.get_db()
    
    cur.execute(
        """
        INSERT INTO idfeed (alias_id, user, description, accurate, inaccurate, mid) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [id, data["username"], data["description"], data[ACCURATE], data[INACCURATE], data[CANT_TELL]]
    )
    
def updateValue(data, voteVal):
    id = data["id"]
    cur = fablesite.model.get_db()
    
    if voteVal == ACCURATE:
        cur.execute(
            "UPDATE feedback SET accurate = accurate + 1 WHERE alias_id = %s",
            [id]
        )
    elif voteVal == CANT_TELL:
        cur.execute(
            "UPDATE feedback SET mid = mid + 1 WHERE alias_id = %s",
            [id]
        )
    elif voteVal == INACCURATE:
        cur.execute(
            "UPDATE feedback SET inaccurate = inaccurate + 1 WHERE alias_id = %s",
            [id]
        )
    else:
        raise Exception("Invalid voteVal")

@fablesite.app.route('/api/v1/get_all_aliases', methods = ['GET'])
def all_aliases():
    """Display / route."""
    try:
        # Connect to database
        cur = fablesite.model.get_db()

        # Query database
        cur.execute(
            "SELECT * FROM aliases"
        )
        
        aliasInfo = cur.fetchall()
        
        # aliasInfo = [
        #     {
        #         "alias": "test1",
        #         "link": "https://www.google.com",
        #         "article": "https://www.google.com",
        #         "id": "1"
        #     },
        #                 {
        #         "alias": "http://en.mercopress.com/2006/09/21/new-york-reacts-calls-chavez-oil-pimp-and-un-cheap-bordello",
        #         "link": "http://en.mercopress.com/2006/09/21/new-york-reacts-calls-chavez-oil-pimp-and-un-cheap-bordello",
        #         "article": "http://en.mercopress.com/2006/09/21/new-york-reacts-calls-chavez-oil-pimp-and-un-cheap-bordello",
        #         "id": "2"
        #     },
        # ]
        
        return flask.jsonify(aliasInfo)
        
    except Exception as e:
        print(e)
        flask.abort(500)

@fablesite.app.route('/api/v1/get_alias/<id>', methods = ['GET'])
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
            [id]
        )

        aliasInfo = cur.fetchone()
        
        return flask.jsonify(aliasInfo)
    
    except Exception as e:
        print(e)
        flask.abort(500)

@fablesite.app.route('/api/v1/post_alias/<id>', methods = ['POST'])
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


@fablesite.app.route('/api/v1/post_aliases/', methods = ['POST'])
def post_aliases():
    """Display / route."""
    data = flask.request.get_json()
    
    try:
        for row in data:
            newRow = {
                "id": row["id"],
                "username": "",
                "description": row["feedbackInput"],
                "quality": row["feedbackSelection"],
                ACCURATE: int(row["feedbackSelection"] == ACCURATE),
                CANT_TELL: int(row["feedbackSelection"] == CANT_TELL),
                INACCURATE: int(row["feedbackSelection"] == INACCURATE)
            }

            addFeedback(newRow)
            updateValue(newRow, newRow["quality"])
        
        return flask.jsonify(success=True)
    
    except Exception as e:
        print(e)
        flask.abort(500)