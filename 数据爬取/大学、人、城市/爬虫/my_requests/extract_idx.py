# https://baike.baidu.com/item/清华大学/111764
# https://baike.baidu.com/api/searchui/suggest?enc=utf8&wd=北京大学
import json
import time
import requests
import random

QUERY_URL = "https://baike.baidu.com/api/searchui/suggest?enc=utf8&wd=%s"
LEMMA_URL = "https://baike.baidu.com/item/%s/%s"

# 加载学校和索引
with open("../baike/distributed/u_idx_name.csv", "r", encoding="utf8") as r:
    u = r.readlines()
u = [_u.strip("\n").split(",") for _u in u]

# 加载ua
with open("../baike/fake/user_agent.txt", mode="r", encoding="utf8") as r:
    user_agent_list = r.readlines()
user_agent = [user_agent.strip("\n") for user_agent in user_agent_list]
total = len(u)
lemma_list = []
lemma_loss = []
status_code = -1
for i, [idx, name] in enumerate(u):
    while status_code != 200:
        response = requests.get(
            url=QUERY_URL % (name), headers={"User-Agent": random.choice(user_agent)}
        )
        status_code = response.status_code
        if response.status_code == 200:
            query_list = json.loads(response.content)["list"]
            if len(query_list) != 0:
                lemmaId = query_list[0]["lemmaId"]
                lemmaTitle = query_list[0]["lemmaTitle"]
                lemma_list.append(str(idx) + "," + LEMMA_URL % (lemmaTitle, lemmaId))
            else:
                lemma_loss.append(str(idx) + "," + str(name))
        time.sleep(random.Random().randint(0, 2))
    status_code = -1
    print("count:%s, total:%s" % (i + 1, total))

with open("lemma_list.txt", "w", encoding="utf8") as w:
    w.write("\n".join(lemma_list))
with open("lemma_loss.txt", "w", encoding="utf8") as w:
    w.write("\n".join(lemma_loss))
