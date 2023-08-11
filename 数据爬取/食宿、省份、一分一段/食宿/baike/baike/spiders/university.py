from scrapy_redis.spiders import RedisSpider

from baike.items import UniversityItem
import scrapy
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import random


# class University(RedisSpider):
#     name = "university"
#     # allow_domains = ["www.baidu.com"]
#     # start_urls = ["https://www.baidu.com"]
#     redis_key = "uni:start_urls"

#     def parse(self, response):
#         item = UniversityItem()
#         name = response.xpath(
#             '//span[@class="line1-schoolName"]/text()'
#         ).extract_first()
#         if name is None:
#             return
#         item["name"] = name
#         location = response.xpath(
#             '//span[@class="line1-province"]/text()'
#         ).extract_first()
#         item["location"] = location if location is not None else []
#         tags = response.xpath('//div[@class="line2 clearfix"]/div')
#         tags = [tag.xpath("text()").extract_first() for tag in tags]
#         item["tags"] = tags
#         web = response.xpath(
#             '//div[@class="line3"]/div[1]//span[@class="school-info-label"]/a/@href'
#         ).extract()
#         item["web"] = web
#         phone = response.xpath(
#             '//div[@class="line3"]/div[2]//span[@class="school-info-label"]/text()'
#         ).extract_first()
#         # phone: '官方电话：023-65102371,023-65102370'
#         item["phone"] = phone.split("：")[-1].split(",")
#         mail = response.xpath(
#             '//div[@class="mailAndqq"]//span[@class="school-info-label"]/text()'
#         ).extract_first()
#         item["mail"] = mail
#         print(dict(item))


class University(scrapy.Spider):
    name = "university"
    allow_domains = ["gaokao.cn"]
    # start_urls = ["https://www.gaokao.cn/school/119"]
    start_urls = []
    with open("u_page.txt", "r") as f:
        for url in f.readlines():
            url = url.rstrip('\n') + '/schoollife'
            start_urls.append(url)
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

    # proxy = ['114.231.41.125:8888'
    #          '123.169.36.132:9999'
    #          '222.74.73.202:42055'
    #          '183.236.232.160:8080'
    #          '114.232.110.5:8888'
    #          '180.120.214.9:8888'
    #          '218.75.102.198:8000'
    #          '182.34.103.237:9999'
    #          '111.3.102.207:30001'
    #          '114.231.46.79:8888'
    #          '36.134.91.82:8888'
    #          '117.68.194.137:9999']

    def parse(self, response):
        item = UniversityItem()

        # ID
        item["ID"] = response.url.split("/")[-1]

        # name
        name = response.xpath(
            '//span[@class="line1-schoolName"]/text()'
        ).extract_first()
        if name is None:
            return
        item["name"] = name

        # image_urls
        image_urls = response.xpath(
            '//div[@class="swiper-wrapper"]//div[@class="video-box"]/img[1]/@src'
        ).extract()
        item["image_urls"] = image_urls

        # location
        location = response.xpath(
            '//span[@class="line1-province"]/text()'
        ).extract_first()
        item["location"] = location if location is not None else []

        # tags
        tags = response.xpath('//div[@class="line2 clearfix"]/div')
        tags = [tag.xpath("text()").extract_first() for tag in tags]
        item["tags"] = tags

        # web
        web = response.xpath(
            '//div[@class="line3"]/div[1]//span[@class="school-info-label"]/a/@href'
        ).extract()
        item["web"] = web

        # phone
        phone = response.xpath(
            '//div[@class="line3"]/div[2]//span[@class="school-info-label"]/text()'
        ).extract_first()
        # phone: '官方电话：023-65102371,023-65102370'
        item["phone"] = phone.split("：")[-1].split(",")

        # mail
        mail = response.xpath(
            '//div[@class="mailAndqq"]//span[@class="school-info-label"]/text()'
        ).extract_first()
        item["mail"] = mail

        # rank
        rank_name = response.xpath(
            '//div[@class="shcool-rank_rankWrap___S-SY"]//div[@class="shcool-rank_name__2sDYc"]/text()'
        ).extract()
        rank_score = response.xpath(
            '//div[@class="shcool-rank_rankWrap___S-SY"]//div[@class="shcool-rank_num__2vcEf"]/span/text()'
        ).extract()
        rank = {name: score for name, score in zip(rank_name, rank_score)}
        item["rank"] = rank

        # baseInfo
        top_info_key = response.xpath(
            '//div[@class="base_info_item_top clearfix"]/div/p/text()'
        ).extract()
        top_info_value = response.xpath(
            '//div[@class="base_info_item_top clearfix"]/div/div[1]|//div[@class="base_info_item_top clearfix"]/div/h3'
        )
        topInfo = {}
        for key, value in zip(top_info_key, top_info_value):
            if value.xpath("div").extract_first() is not None:
                level_list = value.xpath("div/p[2]/text()").extract()
                num_list = value.xpath("div/p[1]/span[1]/text()").extract()
                topInfo[key] = {level: num for level, num in zip(level_list, num_list)}
            else:
                topInfo[key] = value.xpath("text()").extract_first()
        item["topInfo"] = topInfo

        # buildTime
        buildTime = response.xpath(
            '//div[@class="base_info_item_bottom"]/ul/li[1]/span[1]/text()'
        ).extract()
        buildTime = "".join(buildTime).split("：")[-1]
        item["buildTime"] = buildTime

        # detailLocation
        detailLocation = response.xpath(
            '//div[@class="base_info_item_bottom"]/ul/li[3]/span[1]/text()'
        ).extract()
        detailLocation = "".join(detailLocation).split("：")[-1]
        item["detailLocation"] = detailLocation

        # print(dict(item))
        # https://www.gaokao.cn/school/119/introDetails

    def parse_detail(self, response):
        item = UniversityItem()
        # 学院介绍
        # ID
        item["ID"] = response.url.split("/")[-1]
        # crawl introDetails

    # 其他人事
    def parse_professional(self, response):
        item = UniversityItem()
        # 专业
        # https://www.gaokao.cn/school/119/professional
        # ID
        item["ID"] = response.url.split("/")[-1]
        # crawl professional

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_accommodation)
        pass

    def parse_accommodation(self, response):
        item = UniversityItem()
        # 食宿
        # https://www.gaokao.cn/school/119/schoollife
        # ID
        start_index = response.url.find("/school/") + len("/school/")
        end_index = response.url.find("/", start_index)
        item["ID"] = response.url[start_index:end_index]
        driver = uc.Chrome(driver_executable_path='chromedriver.exe', headless=True)
        driver.get(response.url)
        time.sleep(3)
        dormitory = driver.find_element(By.CSS_SELECTOR,
                                        'div.school-life_des__LbxxY>div:nth-child(2)').text
        canteen = driver.find_element(By.CSS_SELECTOR,
                                      'div.school-life_des__LbxxY.school-life_active__3zoEt > div:nth-child(2)').text
        item['dormitory'] = dormitory
        item['canteen'] = canteen
        img = []
        for i in driver.find_elements(By.CSS_SELECTOR,
                                      'div.school-life_pics__2mA0R>img'):
            img.append(i.get_attribute('src'))
        img = json.dumps(img)
        item['img'] = img
        yield item
        driver.quit()
        pass

    def parse_sturule(self, response):
        item = UniversityItem()
        # 招生政策
        # https://www.gaokao.cn/school/119/sturule
        # ID
        item["ID"] = response.url.split("/")[-1]
