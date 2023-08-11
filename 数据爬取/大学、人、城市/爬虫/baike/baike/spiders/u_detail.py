from scrapy_redis.spiders import RedisSpider

from baike.items import UDItem
import scrapy


class UDetail(RedisSpider):
    name = "u_detail"
    # allow_domains = ["www.baidu.com"]
    # start_urls = ["https://www.baidu.com"]
    redis_key = "ud:start_urls"
    count = 0

    def parse(self, response):
        item = UDItem()
        try:
            # https://www.gaokao.cn/school/119/introDetails
            item["ID"] = response.url.split("/")[-2]
            # 学院介绍
            # crawl introDetails
            intro = response.xpath(
                '//div[@class="intro_details_content"]//p/text()|'
                '//div[@class="intro_details_content"]//span/text()'
            ).extract()
            item["intro"] = intro
            yield item
            self.count += 1
            print("crawl:%d" % (self.count))
            # self.scheduler.update(1)

        except Exception:
            print("Fail url: " + response.url)
            print("retry")
            yield scrapy.Request(url=response.url, callback=self.parse)
