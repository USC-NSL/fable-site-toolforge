import pymysql
import csv

# Database connection parameters
db_config = {
    "host": "tools.db.svc.wikimedia.cloud",
    "user": "s55570",
    "password": "",
    "db": "s55570__FABLE",
    "charset": "utf8mb4",  # Ensure charset is defined for proper encoding
    "cursorclass": pymysql.cursors.DictCursor,  # Use DictCursor to fetch rows as dictionaries
}

# SQL query to execute
query = "SELECT * FROM aliases"

# CSV output file path
output_file = "aliases_backup.csv"

# Connect to the database
conn = pymysql.connect(**db_config)

try:
    with conn.cursor() as cursor:
        # Execute the query
        cursor.execute(query)

        # Fetch the results
        result = cursor.fetchall()

        # Get column headers
        headers = (
            result[0].keys() if result else []
        )  # Column names from the first row's keys

        # Write to CSV file
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # write the headers
            for row in result:
                writer.writerow(row.values())  # write the data

finally:
    # Close the database connection
    conn.close()

print(f"Data exported to '{output_file}' successfully.")
