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

node = py2neo.Node()
# label, property
keys = ["id", "title", "infoDict", "intro", "tag"]

table = "special_policy"
sql = "select " + ",".join(keys) + " from " + table

cursor.execute(sql)
uni = cursor.fetchall()

for d in tqdm(uni):
    _u = {k: v for k, v in zip(keys, d)}
    node = py2neo.Node("policy", table, **_u)
    graph.create(node)


cursor.close()
conn.close()
