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
data = pd.read_json("./data/major.json")
data = list(data.T.to_dict().values())
for d in tqdm(data):
    cursor.execute(
        """
    insert into major values(
        %(id)s, %(name)s, %(mainBranch)s, %(subBranch)s, %(duration)s, %(careerInfo)s
        )
    """,
        d,
    )
cursor.close()
conn.commit()
conn.close()
