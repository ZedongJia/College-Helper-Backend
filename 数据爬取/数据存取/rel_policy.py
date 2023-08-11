import json
import pymysql
with open('./data/rel_policy.json', 'r', encoding='utf8') as r:
    data = json.load(r)
MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
for _d in data:
    cursor.execute(
        """
        insert into `college_helper`.`rel_university_special_policy` values(
        %(schoolId)s, %(policyId)s
        )
        """,
        _d
    )
conn.commit()
conn.close()
cursor.close()
