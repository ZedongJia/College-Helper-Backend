import json
from lxml import etree
from utils.proxy import PROXY
import os
from requests_html import HTMLSession
import pymysql
from baike.baike import settings
import urllib.parse

curr_dir = os.path.abspath(os.path.dirname(__file__))

# 新建代理类
proxy = PROXY()

personType = ["知名校友", "知名教师"]
personLink = []


class Person:
    def __init__(self):
        self.session = HTMLSession()
        self.loss = []
        self.nameList = []
        self.conn = pymysql.connect(**settings.MYSQL)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT university_id, name FROM person")
        self.nameList = [str(_t[0]) + str(_t[1]) for _t in self.cursor.fetchall()]

    def getPersonInfo(self, idx, _type, url):
        _n = urllib.parse.unquote(url.split("/")[-2])
        _n = str(idx) + _n
        print("try add:%s" % (_n))
        if _n in self.nameList:
            print("already exists")
            return
        res = self.session.get(url, timeout=20)
        if res.status_code == 200:
            # ----info
            print("get %s" % (res.url))
            # ----
            try:
                html = etree.HTML(res.html.html)
                title = html.xpath("//title/text()")[0]
                if title.find("验证") != -1:
                    print("被反扒")
                    raise Exception
                # 获取个人信息
                # name
                name = html.xpath("//h1/text()")
                name = "".join(name)
                # identity
                identity = _type

                # desc
                desc = html.xpath(
                    '//div[@class="lemma-desc"]/text()|'
                    '//div[@class="lemmaDesc_UzndR"]/text()'
                )
                desc = "".join(desc)

                # intro
                intro = html.xpath(
                    '//div[contains(@class, "J-summary")]//div/text()|'
                    '//div[contains(@class, "J-summary")]/div/text()|'
                    '//div[contains(@class, "J-summary")]//a/text()|'
                    '//div[contains(@class, "J-summary")]/a/text()|'
                    '//div[contains(@class, "J-summary")]//span/text()|'
                    '//div[contains(@class, "J-summary")]/span/text()'
                )
                intro = "".join(intro)

                # infoDict
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

                # store
                self.cursor.execute(
                    """
                    INSERT INTO person
                    VALUES(
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (idx, name, identity, desc, intro, json.dumps(infoDict)),
                )
                self.conn.commit()
                print("add:%s" % name)
            except Exception as e:
                print(e)
                self.loss.append(",".join([str(idx), str(_type), str(url)]))
        else:
            self.loss.append(",".join([str(idx), str(_type), str(url)]))

    def extractPerson(self, idx, url):
        try:
            BASE_URL = "https://baike.baidu.com"
            url = (
                BASE_URL
                + "/item/"
                + url.split("/")[-2]
                + "?fromModule=lemma_search-box"
            )
            response = self.session.get(
                url=url,
                timeout=20,
            )
            if response.status_code == 200:
                # ----info
                print("get %s" % (response.url))
                # ----
                html = etree.HTML(response.html.html)
                title = html.xpath("//title/text()")[0]
                if title.find("验证") != -1:
                    print("被反扒")
                    print("截至idx:%s" % (idx))
                    exit(0)
                keys = html.xpath('//div[contains(@class, "J-basic-info")]//dt')
                values = html.xpath('//div[contains(@class, "J-basic-info")]//dd')
                for key, value in zip(keys, values):
                    _k = key.xpath("./text()")[0].replace("\xa0", "")
                    if _k in personType:
                        hrefs = value.xpath(".//a/@href|./a/@href")
                        for href in hrefs:
                            # (uni_idx, type, person_link)
                            self.getPersonInfo(str(idx), str(_k), str(BASE_URL + href))
                            proxy.random_sleep(5)
        except Exception as e:
            print("fail, error:%s" % e)

    def __del__(self):
        self.session.close()
        self.cursor.close()
        self.conn.close()
        with open("fail.txt", "w", encoding="utf8") as w:
            w.write("\n".join(self.loss))


def main():
    # 自定义
    start = 2575

    # 加载学校，(索引、链接)
    with open(os.path.join(curr_dir, "lemma_list.txt"), "r", encoding="utf8") as r:
        uni = r.readlines()
    uni = [_u.split(",") for _u in uni]

    person = Person()

    for i, [idx, url] in enumerate(uni):
        if i < start:
            continue
        person.extractPerson(idx, url)
        proxy.random_sleep(2)
        print("crawl:%s" % (i + 1))
