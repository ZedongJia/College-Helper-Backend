import json
import pymysql
from tqdm import tqdm

MYSQL1 = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "simugraph",
    "port": 3306,
}
MYSQL2 = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn1 = pymysql.connect(**MYSQL1)
conn2 = pymysql.connect(**MYSQL2)
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()
# 读取city表
with open("./data/city.txt", "r", encoding="utf8") as r:
    citys = r.readlines()
citys = [c.strip("\n").split(",") for c in citys]
citys = {c[1]: c[0] for c in citys}
# 读取university数据
cursor1.execute(
    """
    SELECT ID, location, name, image_urls, buildTime, detailLocation, tags, web, phone, mail, ranking, topInfo, intro
    FROM university
    """
)
university = cursor1.fetchall()
university = [list(u) for u in university]
sche = tqdm(total=len(university))
# 写入university数据
for u in university:
    """
    3,6,7,8,10,11,12
    """
    # json回转
    for i, _u in enumerate(u):
        if i not in [3, 6, 7, 8, 10, 11, 12]:
            if type(_u) == str:
                u[i] = json.loads(_u)
    city = u[1]
    u[1] = citys[city]
    cursor2.execute(
        """
        INSERT INTO university VALUES(
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """,
        u,
    )
    sche.update(1)

conn2.commit()
cursor1.close()
cursor2.close()
conn1.close()
conn2.close()
