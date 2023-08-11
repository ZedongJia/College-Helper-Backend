import py2neo
import pymysql
from tqdm import tqdm

from settings import NEO4J

MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
graph = py2neo.Graph(**NEO4J)
# trans = graph.begin()
node = py2neo.Node()
# label, property
keys = [
    "fk_university_id",
    "fk_major_id",
    "degree",
    "ruanKeScore",
    "detail",
]
table = "rel_major_university"
sql = "select " + ",".join(keys) + " from " + table

cursor.execute(sql)
uni = cursor.fetchall()

for d in tqdm(uni):
    d = [_d if _d is not None else "" for _d in d]
    graph.run(
        "match (a:university),(b:major) where a.id = $fk_university_id and b.id = $fk_major_id merge (a)-[:HAS{fk_university_id:$fk_university_id,fk_major_id:$fk_major_id,degree:$degree,ruanKeScore:$ruanKeScore,detail:$detail}]->(b);",
        {
            "fk_university_id": d[0],
            "fk_major_id": d[1],
            "degree": d[2],
            "ruanKeScore": d[3],
            "detail": d[4],
        },
    )

cursor.close()
conn.close()
