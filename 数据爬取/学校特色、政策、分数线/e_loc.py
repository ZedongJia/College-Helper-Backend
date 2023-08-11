import pandas as pd

'''
读取省份拼音
写入 list[(index, 省份名字),,,], 用\n区分
文件名province_idx.txt
'''
import json
with open('res.json', 'rb') as r:
    raw_data = json.load(r)['data']
    major_data = raw_data['majorScores']
    total_data = raw_data['totalScores']

llist = []
for i, v in enumerate(major_data.keys()):
    llist.append(str(i) + ',' + v + '\n')
f = open("province_idx.txt", "w")
for i in llist:
    f.write(i)

f.close()
