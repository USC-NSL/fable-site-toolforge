import pymysql
import json

# Load your JSON data
with open("data_aliases.json", "r") as file:
    data = json.load(file)

# Database connection parameters
connection_params = {
    "host": "tools.db.svc.wikimedia.cloud",
    "user": "s55570",
    "password": "",
    "db": "s55570__FABLE",
    "cursorclass": pymysql.cursors.DictCursor,
}

# Connect to the database
connection = pymysql.connect(**connection_params)

try:
    with connection.cursor() as cursor:
        # SQL insert statement
        sql = """
        INSERT INTO aliases (article, link, alias)
        VALUES (%s, %s, %s)
        """

        # Loop through the JSON data
        for source, articles in data.items():
            for article in articles:
                # Prepare data for insertion
                insert_data = (article["articleURL"], article["url"], article["alias"])
                # Execute the SQL command
                cursor.execute(sql, insert_data)

        # Commit the changes
        connection.commit()

finally:
    # Close the connection
    connection.close()
