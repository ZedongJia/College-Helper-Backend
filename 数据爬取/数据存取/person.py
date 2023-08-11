import pymysql

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
cursor1.execute(
    """
    SELECT university_id, name, indetity, digest, infoDict, intro
    FROM person
    """
)
person = [list(_tuple) for _tuple in cursor1.fetchall()]
for i, p in enumerate(person):
    cursor2.execute(
        """
        insert into person values(
            null, %s, %s, %s, %s, %s, %s
        )
        """,
        p
    )

conn2.commit()
cursor1.close()
cursor2.close()
conn1.close()
conn2.close()
