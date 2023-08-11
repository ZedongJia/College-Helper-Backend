# 获取专业名称与对应的id
import requests
import json

request_headers = {
    "User-Agent":
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
}

u_link = 'https://static-data.gaokao.cn/www/2.0/info/linkage.json'
resp = requests.get(url=u_link, headers=request_headers)
data = json.loads(resp.text)['data']['special']

with open('special_id.txt', 'w', encoding='utf8') as f:
    for i in data:
        f.write(i['id'] + ',' + i['name'] + '\n')