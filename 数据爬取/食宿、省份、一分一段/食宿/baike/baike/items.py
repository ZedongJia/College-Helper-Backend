# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class UniversityItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 食堂
    ID = Field()
    dormitory = Field()
    canteen = Field()
    img = Field()
    # 地区
    id = Field()
    year = Field()
    type = Field()
    subject = Field()
    line_detail = Field()
    pass
