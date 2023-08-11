import json
import pandas as pd
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
data = pd.read_json("./data/rel_major_university.json")
data = list(data.T.to_dict().values())
print(data[0])
for d in tqdm(data):
    d['detail'] = json.dumps(d['detail'])
    cursor.execute(
        """
    insert into rel_major_university values(
        %(fk_university_id)s, %(fk_major_id)s, %(degree)s, %(ruanKeScore)s, %(detail)s
        )
    """,
        d,
    )
cursor.close()
conn.commit()
conn.close()
