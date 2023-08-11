# 爬取所有大学下的所有专业
import requests
import json
import MySQLdb
import time
from bs4 import BeautifulSoup

start_url = "https://static-data.gaokao.cn/www/2.0/school/"
request_headers = {
    "User-Agent":
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
}

# 0. 连接数据库
conn = MySQLdb.connect(
    host='127.0.0.1',
    user='雨霖铃',
    password='030714hH',
    database='universe_special',
    charset='utf8',
    port=3306,
)
cursor = conn.cursor()

u_page = open('u_page.txt', 'r')
u_page_link = u_page.readlines()
u_page.close()

# 1. 发送请求，获取响应
for link in u_page_link:
    school_id = link.strip().split('/')[-1]
    print(school_id)
    u_link = 'https://static-data.gaokao.cn/www/2.0/school/' + school_id + '/pc_special.json'
    print(u_link)
    resp = requests.get(url=u_link, headers=request_headers)
    dict = json.loads(resp.text)
    print(dict['data'].keys())
    print('学校id：' + school_id)
    if 'special_detail' in dict['data'].keys() and ('1' in dict['data']['special_detail'] or '2' in dict['data']['special_detail']):
        if len(dict['data']['special_detail']['1']) == 0:
            list = dict['data']['special_detail']['2']
        else:
            list = dict['data']['special_detail']['1']
        for special in list:
            special_id = special['special_id']  # 专业id
            special_name =  special['special_name']  # 专业名称
            type_name = special['type_name']  # 层次
            level2_name = special['level2_name']  # 学科门类
            level3_name = special['level3_name']  # 专业类别
            limit_year = special['limit_year'] # 学制
            # 专业详情
            url_detail = start_url + school_id + '/special/' + str(special['id']) + '.json'
            special_detail = json.loads(requests.get(url=url_detail, headers=request_headers).text)['data']['content']
            # 插入数据库
            cursor.execute('insert into special(school_id, special_id, special_name, special_rank, special_category, special_type, special_time, special_detail) values(%s, %s, %s, %s, %s, %s, %s, %s);', (school_id, special_id, special_name, type_name, level2_name, level3_name, limit_year, special_detail))
            conn.commit()
    else:
        # 插入数据库
        cursor.execute('insert into special(school_id) values(%s);', (school_id,))
        conn.commit()


# 关闭数据库连接
conn.close()