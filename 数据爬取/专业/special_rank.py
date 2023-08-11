from requests_html import HTMLSession
from bs4 import BeautifulSoup
import MySQLdb
import random
from random import randint

request_headers = {
    "User-Agent":
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
}

proxy = [
    {
        'http': 'http://182.101.207.11:8080'
    },
    {
        'http': 'http://114.232.109.153:8888'
    },
    {
        'http': 'http://58.20.184.187:9091'
    },
    {
        'http': 'http://114.232.110.72:8888'
    },
    {
        'http': 'http://183.64.239.19:8060'
    },
    {
        'http': 'http://36.134.91.82:8888'
    },
    {
        'http': 'http://223.241.78.103:1133'
    }
]
t = randint(0, 6)
# 读取专业id与专业名称
u_special = open('special_id.txt', 'r', encoding='utf8')
u_special_info = u_special.readlines()
u_special.close()
# 读取大学id与大学名称，以字典储存
u = open('u_idx_name.txt', 'r', encoding='utf8')
u_info = u.readlines()
u.close()
u_info_dict = {}
for item in u_info:
    u_info_dict[item.strip().split(',')[1]] = item.strip().split(',')[0]
# 连接数据库
conn = MySQLdb.connect(
    host='127.0.0.1',
    user='雨霖铃',
    password='030714hH',
    database='special_rank',
    charset='utf8',
    port=3306,
)
cursor = conn.cursor()

# 读取该专业的各大院校评分
for special_info in u_special_info:
    special_id = special_info.strip().split(',')[0]
    special_name = special_info.strip().split(',')[1]
    special_url = 'https://www.gaokao.cn/special/' + special_id + '?special_type=3&sort=3'
    # 开始抓取该专业排名页面
    session = HTMLSession()
    res = session.get(url=special_url, headers=request_headers, timeout=(2, 5), verify=False, proxies=proxy[t])
    res.html.render(sleep=2, retries=3)
    # 获得首页，查看共有多少跳转页
    # 注：只有主页时没有page页数，即主页要单独处理一下
    html_text_index = res.html.html
    soup_doc_index = BeautifulSoup(html_text_index, "lxml")
    print(special_name + '正在录入...')
    # 先判断页面中是否有数据
    isNull = soup_doc_index.select('#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div > div > img')
    if len(isNull) == 1:
        # 该页面无数据
        # 插入数据库
        cursor.execute('insert into special_rank(special_id, special_name) values(%s, %s);', (special_id, special_name))
        conn.commit()
    else:
        # 处理主界面，需要对主界面做些处理，所以与后续界面分开
        school_names = soup_doc_index.select("#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div:nth-child(1) > div > div.school-tab_schoolInfo__1mNye > div.school-tab_title__2GGOk > h3")
        special_scores = soup_doc_index.select("#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div:nth-child(1) > div > div.school-tab_schoolInfo__1mNye > div.school-tab_rankRightInfo__kYTo7")
        print('Page1', end="  ")
        for index in range(len(school_names)):
            school_name = school_names[index].get_text().strip()
            # 根据 school_name 找到相应的 school_id
            school_id = u_info_dict[school_name]
            # 评分
            special_score = special_scores[index].get_text().strip()
            # 插入数据库
            cursor.execute('insert into special_rank(special_id, special_name, school_id, school_name, special_score) values(%s, %s, %s, %s, %s);', (special_id, special_name, school_id, school_name, special_score))
            conn.commit()
        
        # 有数据，进行下一步，判断是否只有一个页面，因为如果只有1个页面的话无法获取page
        page = soup_doc_index.select('#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div.laypage > div > ul > li.ant-pagination-item > a')
        if len(page) == 0:
            # 只有1个界面
            pass
        else:
            # 不止一个界面，进行下一步  读取数据 + 跳转页面
            allPage = page[-1].get_text().strip()
            for page_num in range(1, int(allPage)):
                print('Page' + str(page_num), end="  ")
                # 一次一次的跳转
                res.html.render(sleep=1.5*page_num, retries=3, script="""
                    var i = 0
                    var all_link_num = %d
                    var timer = setInterval(nextPage, 0, all_link_num)
                    function nextPage(all_link_num) {
                        if (i < all_link_num) {
                            const link = document.querySelector("#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div.laypage > div > ul > li.ant-pagination-next > span")
                            link.click()
                            i = i + 1
                        } else {
                            clearInterval(timer)
                        }
                    }
                """%(page_num,))
                html_text = res.html.html
                soup_doc = BeautifulSoup(html_text, "lxml")

                school_names = soup_doc.select("#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div:nth-child(1) > div > div.school-tab_schoolInfo__1mNye > div.school-tab_title__2GGOk > h3")
                special_scores = soup_doc.select("#root > div > div.container > div > div > div:nth-child(1) > div.main.set_main > div.content-box-setmajor > div.left-bar > div > div > div > div > div.ant-tabs-content.ant-tabs-content-no-animated.ant-tabs-top-content.ant-tabs-card-content > div.ant-tabs-tabpane.ant-tabs-tabpane-active > div.school-tab_majorSetUpWrap__3823a > div.school-tab_listBox__1O6Yk > div:nth-child(1) > div > div.school-tab_schoolInfo__1mNye > div.school-tab_rankRightInfo__kYTo7")
                for index in range(len(school_names)):
                    school_name = school_names[index].get_text().strip()
                    # 根据 school_name 找到相应的 school_id
                    school_id = u_info_dict[school_name]
                    # 评分
                    special_score = special_scores[index].get_text().strip()
                    # 插入数据库
                    cursor.execute('insert into special_rank(special_id, special_name, school_id, school_name, special_score) values(%s, %s, %s, %s, %s);', (special_id, special_name, school_id, school_name, special_score))
                    conn.commit()
            print()
# 断开数据库连接
conn.close()