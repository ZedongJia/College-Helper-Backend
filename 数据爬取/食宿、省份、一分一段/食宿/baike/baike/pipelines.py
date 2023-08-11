# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


class BaikePipeline:
    @classmethod
    def from_crawler(cls, crawler):
        cls.MYSQL_HOST = crawler.settings.get('MYSQL_HOST')
        cls.MYSQL_PORT = crawler.settings.get('MYSQL_PORT')
        cls.MYSQL_USER = crawler.settings.get('MYSQL_USER')
        cls.MYSQL_PASSWORD = crawler.settings.get('MYSQL_PASSWORD')
        cls.MYSQL_DBNAME = crawler.settings.get('MYSQL_DBNAME')
        cls.MYSQL_CHARSET = crawler.settings.get('MYSQL_CHARSET')
        return cls()

    def __init__(self):
        self.db = pymysql.connect(host=self.MYSQL_HOST, port=self.MYSQL_PORT, user=self.MYSQL_USER,
                                  passwd=self.MYSQL_PASSWORD,
                                  db=self.MYSQL_DBNAME, charset=self.MYSQL_CHARSET)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        sql1 = "INSERT INTO accommodation (id, dormitory, canteen, img) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql1, (item['ID'],
                                   item['dormitory'],
                                   item['canteen'],
                                   item['img']))

        self.db.commit()
        return item
