import json
import pymysql

with open("./data/policy.json", "r", encoding="utf8") as r:
    policys = json.load(r)


MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
for _p in policys:
    _p['infoDict'] = json.dumps(_p['infoDict'])
    cursor.execute(
        """
        insert into special_policy values(
        %(id)s, %(title)s, %(infoDict)s, %(intro)s, %(des)s
        )
        """,
        _p
    )

conn.commit()
conn.close()
cursor.close()
