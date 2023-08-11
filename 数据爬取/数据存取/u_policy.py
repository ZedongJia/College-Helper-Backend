import json
import pymysql
from tqdm import tqdm
MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
with open("./data/major_score_clean.json", "r", encoding="utf8") as r:
    data = json.load(r)
for d in tqdm(data):
    d['batch'] = d['batch'][0]
    d['detail'] = json.dumps(d['detail'])
    cursor.execute(
        """
    insert into university_policy values(
        %(fk_university_id)s,
        %(fk_province_id)s,
        %(branch)s,
        %(batch)s,
        %(detail)s
    )
    """,
        d,
    )
with open("./data/total_score_clean.json", "r", encoding="utf8") as r:
    data = json.load(r)
for d in tqdm(data):
    d['batch'] = d['batch'][0]
    d['detail'] = json.dumps(d['detail'])
    cursor.execute(
        """
    insert into university_policy values(
        %(fk_university_id)s,
        %(fk_province_id)s,
        %(branch)s,
        %(batch)s,
        %(detail)s
    )
    """,
        d,
    )
cursor.close()
conn.commit()
conn.close()
