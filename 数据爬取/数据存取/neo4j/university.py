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
keys = [
    "id",
    "fk_city_id",
    "name",
    "imageUrls",
    "establishTime",
    "detailLocation",
    "honorTags",
    "officialWebsite",
    "officialPhoneNumber",
    "officialEmail",
    "rankInfo",
    "educationInfo",
    "intro",
]
sql = "select " + ",".join(keys) + " from university"

cursor.execute(sql)
uni = cursor.fetchall()

for d in tqdm(uni):
    _u = {k: v for k, v in zip(keys, d)}
    node = py2neo.Node("university", **_u)
    graph.create(node)


cursor.close()
conn.close()
