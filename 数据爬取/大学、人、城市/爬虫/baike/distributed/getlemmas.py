import json

url = 'https://www.gaokao.cn/school/'
url_list = []
with open('./response.json', 'r', encoding='utf8') as r:
    data = r.read()
dataList = json.loads(data)['data']
for row in dataList:
    school_id = row['school_id']
    url_list.append(url + str(school_id))

with open('crawlPage.txt', 'w', encoding='utf8') as w:
    w.write('\n'.join(url_list))
