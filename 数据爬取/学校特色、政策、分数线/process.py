import json
import pandas as pd
import pymysql
'''
data
    beijing...
        2019-2021
            list
                averageScore: 696
                batch: "本科一批"
                lowScore: "696/21"
                name: "工商管理类"
                type: "理科"
    beijing...
        2019-2021
                batch: "本科一批"
                controlScore: "555"
                lowScore: "--/--"
                type: "理科"
                zslx: '普通类'
school_id ?, province_id, year
    ->'专业分数线', type, name, batch, averageScore, lowScore, 
    ->'学校分数线', type, batch, controlScore, lowScore, enrollmentType
'''
province_map = {}
fp = open('province_idx.txt', 'r')
line = fp.readline()
while line:
    province_map[line.split(",")[1].replace("\n","")] = line.split(",")[0]
    line = fp.readline()
fp.close()


def extract(schoolid,majorscores,totalscores):
    major_data = []
    conn = pymysql.connect(host='localhost',
                           user='newuser',
                           password='newuser',
                           database='cool',
                           charset='utf8')
    cursor = conn.cursor()
    res = []
    for i in majorscores.keys():
        if i == '':
            continue
        std = majorscores[i]
        for year in std.keys():
            for li in std[year]:
                ress = {}
                ress['schoolId'] = schoolid
                ress['provinceId'] = province_map[i]
                ress['year'] = year
                ress['type'] = li['type']
                ress['name'] = li['name']
                ress['batch'] = li['batch']
                ress['averageScore'] = li['averageScore']
                ress['lowScore'] = li['lowScore']
                res.append(ress)

    for re in res:
        cursor.execute("INSERT INTO major_scores (schoolId, provinceId, year, type, name, batch, averageScore, lowScore) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (re['schoolId'], re['provinceId'], re['year'], re['type'], re['name'],re['batch'],re['averageScore'],re['lowScore']))
    conn.commit()
    total = []
    if type(totalscores) == dict:
        for i in totalscores.keys():
            if i == '':
                continue
            std = totalscores[i]
            for year in std.keys():
                for li in std[year]:
                    totalscore = {}
                    totalscore['schoolId'] = schoolid
                    totalscore['provinceId'] = province_map[i]
                    totalscore['year'] = year
                    totalscore['type'] = li['type']
                    totalscore['batch'] = li['batch']
                    totalscore['controlScore'] = li['controlScore']
                    totalscore['lowScore'] = li['lowScore']
                    totalscore['enrollmentType'] = li['zslx']
                    total.append(totalscore)

    cursor = conn.cursor()
    for re in total:
        cursor.execute("INSERT INTO total_scores (schoolId, provinceId, year, type, batch, controlScore, lowScore, enrollmentType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (re['schoolId'], re['provinceId'], re['year'], re['type'], re['batch'], re['controlScore'], re['lowScore'], re['enrollmentType']))
    cursor.close()
    conn.commit()
    conn.close()

