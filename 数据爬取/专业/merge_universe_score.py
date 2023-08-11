import json
import MySQLdb

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

# 插入数据库
# cursor.execute('select special_name, school_id, special_score from special_rank')
# info = cursor.fetchall()
# f = open('info.txt', 'w', encoding='utf8')
# for i in info:
#     f.write(str(i[0]) + ',' + str(i[1]) + ',' + str(i[2]) + '\n')

f = open('info.txt', 'r', encoding='utf8')
content = f.readlines()
f.close()
i = 0
for c_item in content:
    i = i + 1
    print(i)
    temp = c_item.strip().split(',')
    cursor.execute('update special set special.special_score = %s where special_name = %s and school_id = %s', (temp[2], temp[0], temp[1]))
    conn.commit()
conn.close()

    