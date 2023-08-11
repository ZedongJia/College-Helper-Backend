# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import undetected_chromedriver as ud
from scrapy.http import HtmlResponse
import time
# useful for handling different item types with a single interface
# from scrapy.exceptions import IgnoreRequest, CloseSpider


class RandomDelay:
    def process_request(self, request, spider):
        time.sleep(random.Random().randint(1, 3))
        return None


class DynamicRenderMiddleware:
    def __init__(self) -> None:
        self.driver = ud.Chrome(headless=True)

    def process_request(self, request, spider):
        return self.render(request)

    def render(self, request):
        self.driver.get(request.url)
        body = self.driver.page_source
        return HtmlResponse(
            url=request.url, body=body, request=request, encoding="utf8", status=200
        )

    def __del__(self):
        self.driver.close()
        self.driver.quit()


class ProxyMiddleware:
    def __init__(self) -> None:
        self.ip_pool = []
        self.user_agent = []
        self.curr_ip = ""
        self.initialize_ip_pool("fake/ip.txt")
        print("successfully load ip pool")
        self.initialize_user_agent("fake/user_agent.txt")
        print("successfully load user agent pool")

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        request.headers["User-Agent"] = random.choice(self.user_agent)
        # if len(self.ip_pool) == 0:
        #     print("WARNING: 当前IP池为空")
        #     exit(0)
        # self.curr_ip = random.choice(self.ip_pool)
        # # 设请求代理
        # request.meta["proxy"] = "http://" + self.curr_ip
        return None

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # 移除当前ip
        if len(self.ip_pool) == 0:
            print("WARNING: 当前IP池为空")
            self.curr_ip = ""
            exit(0)
        print("WARNING: 无效ip:%s" % (self.curr_ip))
        self.remove_curr_ip()
        # 随机选择下一个ip
        self.curr_ip = random.choice(self.ip_pool)
        # 重设请求代理
        request.meta["proxy"] = "http://" + self.curr_ip
        return request

    def initialize_ip_pool(self, filepath):
        self.filepath = filepath
        with open(filepath, mode="r", encoding="utf8") as r:
            ip_list = r.readlines()
        self.ip_pool = [ip.strip("\n") for ip in ip_list]

    def initialize_user_agent(self, filepath):
        with open(filepath, mode="r", encoding="utf8") as r:
            user_agent_list = r.readlines()
        self.user_agent = [user_agent.strip("\n") for user_agent in user_agent_list]

    def remove_curr_ip(self):
        self.ip_pool.remove(self.curr_ip)
        print("INFO: " + "当前IP池剩余:%d" % (len(self.ip_pool)))

    def __del__(self):
        with open(self.filepath, mode="w", encoding="utf8") as w:
            w.write("\n".join(self.ip_pool))
