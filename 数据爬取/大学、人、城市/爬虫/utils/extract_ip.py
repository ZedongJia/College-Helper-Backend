import requests
from lxml import etree

url = "http://www.ip3366.net/free/?stype=1&page=%d"  # (1, 7)
ip_list = []
for i in range(1, 7):
    uurl = url % (i)
    response = requests.get(url=uurl)
    if response.status_code == 200:
        html = etree.HTML(response.text)
        ip_row = html.xpath("//tbody/tr")
        for _ip in ip_row:
            ip_4 = _ip.xpath("./td[1]/text()")
            if len(ip_4) == 0:
                break
            ip_4 = ip_4[0]
            ip_port = _ip.xpath("./td[2]/text()")[0]
            ip_type = _ip.xpath("./td[4]/text()")[0]
            ip_list.append(ip_type.lower() + '://' + ip_4 + ":" + ip_port)


# 测试ip是否可用


with open("./res/ip.txt", "w", encoding="utf8") as w:
    w.write("\n".join(ip_list))
