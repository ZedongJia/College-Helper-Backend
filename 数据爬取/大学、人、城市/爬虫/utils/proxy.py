import time
from typing import overload
from urllib.request import Request
from datetime import datetime
import random
import os

MAX_SLEEP_TIME = 2


class PROXY:
    r"""
    this is an auto adding proxy ip & user_agent class
    """

    def __init__(self) -> None:
        self.set_rand()
        self._http_pool = []
        self._https_pool = []
        self._user_agent_pool = []
        self.curr_dir = os.path.abspath(os.path.dirname(__file__))
        self._load_ip()
        self._load_user_agent()

    def set_rand(self, seed: int = -1):
        r"""
        set random seed
        """
        if seed == -1:
            seed = datetime.now().second
        self.random = random.Random(int(seed))

    @overload
    def polish(self, request: Request):
        r"""
        required a request object
        """
        request.add_header("User-Agent", self.random_user_agent())
        request.set_proxy(self.random_ip(), "http")
        return request

    @overload
    def polish(self) -> dict:
        r"""
        return a dict contains ip & user-agent
        """
        return {"ip": self.random_ip(), "user-agent": self.random_user_agent()}

    def random_user_agent(self) -> str:
        ua = self.random.choice(self._user_agent_pool)
        return ua

    def random_ip(self, __type: str = "http") -> str:
        ip = (
            self.random.choice(self._http_pool)
            if __type == "http"
            else self.random.choice(self._https_pool)
        )
        return ip

    def _load_ip(self):
        with open(
            os.path.join(self.curr_dir, "res", "ip.txt"), "r", encoding="utf8"
        ) as r:
            ip = r.readlines()
        for _ip in ip:
            _ip = _ip.strip('\n')
            if _ip.find("http:") != -1:
                self._http_pool.append(_ip)
            elif _ip.find("https:") != -1:
                self._https_pool.append(_ip)

    def _load_user_agent(self):
        with open(
            os.path.join(self.curr_dir, "res", "user_agent.txt"), "r", encoding="utf8"
        ) as r:
            u_a = r.readlines()
        self._user_agent_pool = [_u.strip("\n") for _u in u_a]

    def random_sleep(self, max: int = MAX_SLEEP_TIME):
        time.sleep(self.random.randint(1, max))
