import random
import time
import requests
import json
import pymysql

# url = "https://static-data.gaokao.cn/www/2.0/special/1130/pc_special_detail.json"
MYSQL = {
    "host": "localhost",
    "user": "j",
    "password": "j",
    "database": "simuGraph",
    "port": 3306,
}


class Career:
    def __init__(self):
        self.base_url = (
            "https://static-data.gaokao.cn/www/2.0/special/%s/pc_special_detail.json"
        )
        with open("./major_idx.txt", "r", encoding="utf8") as r:
            majors = r.readlines()
        self.major_idx = [_m.strip("\n").split(",")[0] for _m in majors]
        self.loss = []
        self.conn = pymysql.connect(**MYSQL)
        self.cursor = self.conn.cursor()

    def run(self):
        self.extract()

    def extract(self):
        # data
        #   do_what
        for i, idx in enumerate(self.major_idx):
            try:
                response = requests.get(url=self.base_url % str(idx))
                if response.status_code == 200:
                    data = json.loads(response.content)
                    major_emp = data["data"]["do_what"]
                    self.cursor.execute(
                        "INSERT INTO major_idx values(%s, %s)", (idx, major_emp)
                    )
                    self.conn.commit()
                else:
                    self.loss.append(",".join([str(idx), self.base_url % str(idx)]))
                time.sleep(random.Random().randint(1, 3))
            except Exception as e:
                print(e)
                self.loss.append(",".join([str(idx), self.base_url % str(idx)]))
            print("loop:%s" % i)

    def __del__(self):
        with open("major_fail.txt", "w", encoding="utf8") as w:
            w.write("\n".join(self.loss))
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    c = Career()
    c.run()
