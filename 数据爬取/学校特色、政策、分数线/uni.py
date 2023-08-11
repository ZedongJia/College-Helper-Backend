'''
请求url
获取json
传入extract函数
'''
import json
import time
import random

from process import extract
import requests
# lemma = []
# le = []
# fp = open('lemma_list.txt', 'r', encoding='utf-8')
# line = fp.readline()
# while line:
#     lemma.append(line.replace("\n","").split(","))
#     line = fp.readline()
# fp.close()

fail = []
fp = open('fail2.txt', 'r', encoding='utf-8')
line = fp.readline()
while line:
    fail.append(line.split(","))
    line = fp.readline()
fp.close()


total = 0
loss = []
for lem in fail:
    # le = lem[1].split("/")
    # url = 'https://baike.baidu.com/wikiui/api/getscoreline?lemmaId=%s&lemmaTitle=%s' % (le[-1], le[-2])
    url = lem[1]
    print(url)
    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('data', None) is not None:
                major_data = data['data']['majorScores']
                total_data = data['data']['totalScores']
                extract(lem[0], major_data, total_data)
            time.sleep(random.random()*3)
            total += 1
            print('crawl:%d' % total)
    except Exception as e:
        print(e)
        loss.append(str(lem[0]) + ',' + url)

with open('fail3.txt', 'w', encoding='utf8') as w:
    w.write('\n'.join(loss))
