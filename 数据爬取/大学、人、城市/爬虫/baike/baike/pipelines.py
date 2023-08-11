# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import pymysql
from baike.settings import MYSQL


class BaikePipeline:
    def __init__(self) -> None:
        self.conn = pymysql.connect(**MYSQL)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS university(
                ID INT,
                name VARCHAR(100),
                image_urls TEXT,
                buildTime VARCHAR(20),
                location TEXT,
                detailLocation TEXT,
                tags TEXT,
                web TEXT,
                phone TEXT,
                mail TEXT,
                ranking TEXT,
                topInfo TEXT,
                intro LONGTEXT,
                PRIMARY KEY(ID)
            );
            """
        )

    def process_item(self, item, spider):
        _dict = {k: json.dumps(v) for k, v in dict(item).items()}
        try:
            self.cursor.execute(
                """
                INSERT INTO university values(
                    %(ID)s,
                    %(name)s,
                    %(image_urls)s,
                    %(buildTime)s,
                    %(location)s,
                    %(detailLocation)s,
                    %(tags)s,
                    %(web)s,
                    %(phone)s,
                    %(mail)s,
                    %(ranking)s,
                    %(topInfo)s,
                    %(intro)s
                )
                """,
                _dict,
            )
            self.conn.commit()
        except Exception as e:
            print(e)
            pass
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


class UDPipeline:
    def __init__(self) -> None:
        self.writer = open("res1.json", "w", encoding="utf8")

    def process_item(self, item, spider):
        try:
            self.writer.write(json.dumps(dict(item)) + '\n')
        except Exception:
            pass
        return item

    def close_spider(self, spider):
        self.writer.close()
