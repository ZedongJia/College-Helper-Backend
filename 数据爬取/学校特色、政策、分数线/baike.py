import requests
import pandas as pd
# 专业录取分数
url = 'https://baike.baidu.com/wikiui/api/getscoreline?lemmaId=111764&lemmaTitle=清华大学'
# 一分一段表
# urls = 'https://static-data.gaokao.cn/www/2.0/section2021/2023/14/1/3/lists.json'

response = requests.get(url=url)
if response.status_code == 200:
    with open('res.json', 'wb') as w:
        w.write(response.content)
