import json
import pymysql
import uuid
import sshtunnel


def driver():
    with open("data/permlink_aliases.json", "r") as f:
        data = json.load(f)
        
        for i in data:
            alias = i["alias"]
            link = i["url"]
            article = i["articleURL"]
            id = str(uuid.uuid4().hex)
            
            # Aliases
            cur.execute("INSERT INTO aliases (id, alias, link, article) VALUES (%s, %s, %s, %s)", [id, alias, link, article])

            # Feedback 
            cur.execute("INSERT INTO feedback (alias_id, accurate, inaccurate, mid) VALUES (%s, %s, %s, %s)", [id, 0, 0, 0])
    
    cur.close()
    con.commit()
    
if __name__ == "__main__":
    driver()