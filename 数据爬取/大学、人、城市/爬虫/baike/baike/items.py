# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaikeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class UniversityItem(scrapy.Item):
    ID = scrapy.Field()
    name = scrapy.Field()
    image_urls = scrapy.Field()
    buildTime = scrapy.Field()
    location = scrapy.Field()
    detailLocation = scrapy.Field()
    tags = scrapy.Field()
    web = scrapy.Field()
    phone = scrapy.Field()
    mail = scrapy.Field()
    ranking = scrapy.Field()
    topInfo = scrapy.Field()
    intro = scrapy.Field()


class UDItem(scrapy.Item):
    ID = scrapy.Field()
    intro = scrapy.Field()
