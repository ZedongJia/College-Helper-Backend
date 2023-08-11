import json
import MySQLdb

# 读取专业id与专业名称
u_special = open('special_id.txt', 'r', encoding='utf8')
u_special_info = u_special.readlines()
u_special.close()
s_info_dict = {}
# 以字典的形式存储
for item in u_special_info:
    s_info_dict[item.strip().split(',')[0]] = item.strip().split(',')[1]
# 读取专业idx 与 专业职位信息
with open('career.json', 'r', encoding='utf8') as f:
    content = f.read()
career_infos = json.loads(content)   # 字典数组，有idx与career
f.close()

# 连接数据库
conn = MySQLdb.connect(
    host='127.0.0.1',
    user='雨霖铃',
    password='030714hH',
    database='universe_special',
    charset='utf8',
    port=3306,
)
cursor = conn.cursor()

# 根据 career_infos 中的每一个字典的 idx 找到 special_id.txt中对应的 special_name.txt
i = 0
for c_item in career_infos:
    i = i + 1
    print(i)
    special_name = s_info_dict[str(c_item['idx'])]
    # 插入数据库
    cursor.execute('update special set special.special_info = %s where special_name = %s', (c_item['major_emp'], special_name))
    conn.commit()
conn.close()