import random
import time
import urllib.parse
import pymysql
import requests
from lxml import etree
from requests_html import HTMLSession
import json
from tqdm import tqdm

session = HTMLSession()

conn = pymysql.connect(host='localhost',
                       user='newuser',
                       password='newuser',
                       database='cool',
                       charset='utf8')
cursor = conn.cursor()


cursor.execute("SELECT id, TITLE FROM national_policy")
name_list = {_tuple[1]: _tuple[0] for _tuple in cursor.fetchall()}

cursor.execute("SELECT schoolId, policyId FROM national_school")

idx_list = [','.join([str(_t) for _t in _tuple]) for _tuple in cursor.fetchall()]

def extract_policy(idx, url, title):
    # https://baike.baidu.com/item/211%E5%B7%A5%E7%A8%8B/203547?fromModule=lemma_inlink
    # 'https:', '', 'baike.baidu.com', 'item', '?'
    print(title)
    title_set = set(name_list.keys())
    print(title in title_set)
    if title not in title_set:
        resp = session.get(url=url, timeout=(2, 5), verify=False)
        if resp.status_code != 200:
            return
        html = etree.HTML(resp.html.html)
        title = html.xpath("//h1/text()")
        title = "".join(title)

        desc = html.xpath(
            '//div[@class="lemma-desc"]/text()|'
            '//div[@class="lemmaDesc_UzndR"]/text()'
        )
        desc = "".join(desc)

        intro = html.xpath(
            '//div[contains(@class, "J-summary")]//div/text()|'
            '//div[contains(@class, "J-summary")]/div/text()|'
            '//div[contains(@class, "J-summary")]//a/text()|'
            '//div[contains(@class, "J-summary")]/a/text()|'
            '//div[contains(@class, "J-summary")]//span/text()|'
            '//div[contains(@class, "J-summary")]/span/text()'
        )
        intro = "".join(intro)

        infoDict = {}
        keys = html.xpath('//div[contains(@class, "J-basic-info")]//dt')
        values = html.xpath('//div[contains(@class, "J-basic-info")]//dd')
        for key, value in zip(keys, values):
            _k = key.xpath("./text()")[0].replace("\xa0", "")
            _v = value.xpath(
                ".//a/text()|"
                "./a/text()|"
                ".//i/text()|"
                "./i/text()|"
                ".//span/text()|"
                "./span/text()|"
                "./text()"
            )
            _v = "".join(_v)
            infoDict[_k] = _v.replace("\n", "")

        cursor.execute("INSERT INTO national_policy (title, des, intro, infoDict) VALUES (%s, %s, %s, %s)", (title, desc, intro, json.dumps(infoDict)))
        conn.commit()
        # 查，插入
        cursor.execute("SELECT id, TITLE FROM national_policy where title = (%s)",title)
        result = cursor.fetchall()[0]
        name_list[result[1]]=result[0]

    if ','.join([str(idx), str(name_list[title])]) not in idx_list:
        cursor.execute("INSERT INTO national_school (schoolId, policyId) VALUES (%s, %s)", (idx,name_list[title]))
        conn.commit()


def extract_link(idx, url):
    url = url.split('/')
    url = 'https://baike.baidu.com/item/' + url[-2] + '?fromModule=lemma_search-box'
    response = requests.get(url=url)
    if response.status_code != 200:
        return
    print(response.url)
    html_text = response.text
    xpath_selector = etree.HTML(html_text)
    keys = xpath_selector.xpath('//div[contains(@id, "J-lemma-main-wrapper")]//dt|//div[contains(@class, "J-basic-info")]//dt')
    values = xpath_selector.xpath('//div[contains(@id, "J-lemma-main-wrapper")]//dd|//div[contains(@class, "J-basic-info")]//dd')
    for key, value in zip(keys, values):
        _k = key.xpath("./text()")[0].replace("\xa0", "")
        if _k == '学校特色':
            hrefs = value.xpath(".//a/@href|./a/@href")
            print(hrefs)
            for href in hrefs:
                title = urllib.parse.unquote(href.split('/')[2])
                href = 'https://baike.baidu.com'+href
                extract_policy(idx, href, title)
                time.sleep(random.Random().randrange(0, 1))

    time.sleep(random.Random().randrange(2, 5))


lemma = []
fp = open('lemma_list.txt', 'r', encoding='utf-8')
line = fp.readline()
while line:
    lemma.append(line.split(","))
    line = fp.readline()
fp.close()

start = 2739
total = 2889
for i, (idx, url) in enumerate(lemma):
    if i < start:
        continue
    extract_link(idx, url)
    print('get:%d, total:%d' % (i + 1, total))
