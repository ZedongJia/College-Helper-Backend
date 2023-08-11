import pymysql

MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "college_helper",
    "port": 3306,
}
conn = pymysql.connect(**MYSQL)
cursor = conn.cursor()
with open("./data/city.txt", "r", encoding="utf8") as r:
    citys = r.readlines()
citys = [c.strip("\n").split(",") for c in citys]

with open("./data/province.txt", "r", encoding="utf8") as r:
    provinces = r.readlines()
provinces = [p.strip("\n").split(",") for p in provinces]

# wirte province
for p in provinces:
    cursor.execute(
        """
        INSERT INTO province VALUES(
            %s,%s
        )
        """,
        (p[0], p[1]),
    )

# write city
for c in citys:
    cursor.execute(
        """
        INSERT INTO city VALUES(
            %s,%s,%s
        )
        """,
        (c[0], c[1], c[2]),
    )

cursor.close()
conn.commit()
conn.close()