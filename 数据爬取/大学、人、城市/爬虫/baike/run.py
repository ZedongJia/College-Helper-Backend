from scrapy import cmdline


# cmdline.execute(["scrapy", "runspider", "baike/spiders/u_detail.py"])
cmdline.execute(["scrapy", "crawl", "university"])
