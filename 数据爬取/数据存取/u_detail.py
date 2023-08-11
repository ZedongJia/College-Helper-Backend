import json
import pymysql

MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
with open("./data/output.json", "r", encoding="utf8") as r:
    data = json.load(r)[0]["u_detail:items"]
for d in data:
    d = json.loads(d)
    ID = d["ID"]
    intro = d["intro"]
    if len(intro) == 0:
        continue
    cursor.execute(
        """
        update university set intro=%s where id=%s
        """,
        (json.dumps(intro), ID),
    )
cursor.close()
conn.commit()
conn.close()