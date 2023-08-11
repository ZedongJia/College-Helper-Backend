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
    "id",
    "name",
    "mainBranch",
    "subBranch",
    "duration",
    "careerInfo",
]
table = "major"
sql = "select " + ",".join(keys) + " from " + table

cursor.execute(sql)
uni = cursor.fetchall()

for d in tqdm(uni):
    _u = {k: v if v is not None else "" for k, v in zip(keys, d)}
    if _u["mainBranch"] != "":
        node = py2neo.Node(table, _u["mainBranch"], **_u)
    else:
        node = py2neo.Node(table, **_u)
    graph.create(node)

cursor.close()
conn.close()
