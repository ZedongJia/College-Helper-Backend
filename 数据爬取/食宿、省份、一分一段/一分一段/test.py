import urllib.request
import random
import json
import pymysql

# 爬取一分一段数据

# 连接数据库
db = pymysql.connect(
    host="localhost",
    port=3306,
    user='root',
    database='accommodation',
    password='hxm200307240693',
    charset='utf8mb4'
)
cursor = db.cursor()

# 爬虫
user_agents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
headers = {
    'User-Agent': random.choice(user_agents)
}

# 得到科目类别及其编号

# url.txt文件是自行爬取并对数据整理后方便读取而生成的，但我把代码删了呜呜呜呜呜呜呜
province = []
year = []
type = []
subject = []
url = []
with open('url.txt', 'r', encoding='utf-8') as f:
    for row in f.readlines():
        province.append(row.split(',')[0])
        year.append(row.split(',')[1])
        type.append(row.split(',')[2])
        subject.append(row.split(',')[3])
        url.append(row.strip('\n').split(',')[4])

for p, y, t, s, u in zip(province, year, type, subject, url):
    # 获取地址编号及其名字
    province_name = p.split('(')[1].strip(')')
    province_id = ''
    with open('province_idx.txt', 'r', encoding='utf-8') as f:
        for row in f.readlines():
            id = row.split(',')[0]
            name = row.split(',')[1].strip('\n')
            if province_name == name:
                province_id = id
                break
    # 获取类别
    t = t.split('(')[1].strip(')')

    # 获取专科or本科
    s = s.split('(')[1].strip(')')

    # 获取json
    request = urllib.request.Request(url=u, headers=headers)
    response = urllib.request.urlopen(request)
    data = json.load(response)['data']['list']
    score = []
    score_detail = []
    for temp in data:
        score.append(temp['score'])
        temp.pop('score', None)
        score_detail.append(temp)
    line_detail = dict(zip(score, score_detail))
    line_detail = json.dumps(line_detail)
    # 插入数据库
    sql = "INSERT INTO lineparagraph (id, name, year, type, subject, line_detail) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (province_id, province_name, y, t, s, line_detail))
    db.commit()

cursor.close()
db.close()
