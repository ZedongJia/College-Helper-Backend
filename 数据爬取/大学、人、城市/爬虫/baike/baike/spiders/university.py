# from scrapy_redis.spiders import RedisSpider

from baike.items import UniversityItem
import scrapy
from tqdm import tqdm
import pymysql
from baike import settings


class University(scrapy.Spider):
    name = "university"
    # allow_domains = ["www.baidu.com"]
    # start_urls = ["https://www.baidu.com"]
    # redis_key = "uni:start_urls"

    count_num = 0
    total_num = 0

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        # 获取已爬取ID
        conn = pymysql.connect(**settings.MYSQL)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ID
            FROM university
            """
        )
        _tuple = cursor.fetchall()
        self.visited_IDs = [str(_t[0]) for _t in _tuple]
        cursor.close()
        conn.close()

        # 获取urls列表
        with open("distributed/u_page.txt", "r", encoding="utf8") as r:
            urls = r.readlines()
        self.start_urls = []
        for url in urls:
            url = url.strip("\n")
            ID = url.split("/")[-1]
            if str(ID) in self.visited_IDs:
                continue
            self.start_urls.append(url)
        self.total_num = len(self.start_urls)
        self.scheduler = tqdm(total=self.total_num)

    def parse(self, response):
        try:
            item = UniversityItem()

            # ID
            item["ID"] = int(response.url.split("/")[-1])

            # name
            name = response.xpath(
                '//span[@class="line1-schoolName"]/text()'
            ).extract_first()
            if name is None:
                print(response.url)
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
            item["location"] = location if location is not None else ""

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
            if phone is not None:
                item["phone"] = phone.split("：")[-1].split(",")
            else:
                item["phone"] = ""

            # mail
            mail = response.xpath(
                '//div[@class="mailAndqq"]//span[@class="school-info-label"]/text()'
            ).extract_first()
            item["mail"] = mail if mail is not None else ""

            # rank
            rank_name = response.xpath(
                '//div[@class="shcool-rank_rankWrap___S-SY"]//div[@class="shcool-rank_name__2sDYc"]/text()'
            ).extract()
            rank_score = response.xpath(
                '//div[@class="shcool-rank_rankWrap___S-SY"]//div[@class="shcool-rank_num__2vcEf"]/span/text()'
            ).extract()
            ranking = {name: score for name, score in zip(rank_name, rank_score)}
            item["ranking"] = ranking

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
                    topInfo[key] = {
                        level: num for level, num in zip(level_list, num_list)
                    }
                else:
                    topInfo[key] = value.xpath("text()").extract_first()
            item["topInfo"] = topInfo

            # buildTime
            buildTime = response.xpath(
                '//div[@class="base_info_item_bottom"]/ul/li[1]/span[1]/text()'
            ).extract()
            if buildTime != []:
                buildTime = "".join(buildTime).split("：")[-1]
            else:
                buildTime = ""
            item["buildTime"] = buildTime

            # detailLocation
            detailLocation = response.xpath(
                '//div[@class="base_info_item_bottom"]/ul/li[3]/span[1]/text()'
            ).extract()
            if detailLocation != []:
                detailLocation = "".join(detailLocation).split("：")[-1]
            else:
                detailLocation = ""
            item["detailLocation"] = detailLocation
            yield scrapy.Request(
                url=response.url + "/introDetails",
                callback=self.parse_detail,
                meta={"item": item},
            )
            # https://www.gaokao.cn/school/119/introDetails
        except Exception:
            print("Fail url: " + response.url)
            yield scrapy.Request(
                url=response.url, callback=self.parse, dont_filter=False
            )

    def parse_detail(self, response):
        try:
            # 学院介绍
            item = response.meta["item"]
            # crawl introDetails
            intro = response.xpath(
                '//div[@class="intro_details_content"]//p/text()|'
                '//div[@class="intro_details_content"]//span/text()'
            ).extract()
            item["intro"] = intro
            yield item
            self.scheduler.update(1)

        except Exception:
            print("Fail url: " + response.url)
            print("retry")
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_detail,
                meta={"item": item},
            )
