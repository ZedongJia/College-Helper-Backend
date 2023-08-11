# match (a:university),(b:policy:special_policy) where a.id = ${fk_university_id} and b.id = ${fk_special_id} merge (a)-[:HAS]->(b);
import py2neo
from tqdm import tqdm
import pymysql
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
cursor.execute(
    """
    select fk_university_id, fk_special_id from rel_university_special_policy
    """
)
rel = cursor.fetchall()

graph = py2neo.Graph(**NEO4J)
transaction = graph.begin()
for r in tqdm(rel):
    transaction.run(
        "match (a:university),(b:policy:special_policy) where a.id = $fk_university_id and b.id = $fk_special_id merge (a)-[:HAS]->(b)",
        {"fk_university_id": r[0], "fk_special_id": r[1]},
    )

graph.commit(transaction)
cursor.close()
conn.close()
