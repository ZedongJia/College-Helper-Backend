from neo4j_model.db_pool import NEO4j_POOL
import json
from models.recognize import Recognize
import random

# 获取所有省、市、大学、祖专业、父专业、专业的四个列表
#     # 政策、person、major、university、省份、城市


def get_list(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        info_json = f.read()
    info = json.loads(info_json)
    list = []
    for i in info:
        list.append(i['n.name'])
    f.close()
    return list

province_list = get_list('entity/data/province.json')
city_list = get_list('entity/data/city.json')
province_id_dict = {}
with open('entity/data/province_idx.txt', 'r', encoding='utf8') as f:
    info = f.readlines()
for p_ in info:
    province_id_dict[p_.strip().split(',')[1]] = p_.strip().split(',')[0]


def entityType(temp):
    if temp in province_list:
        return 'province'
    elif temp in city_list:
        return 'city'
    else:
        try:
            t = Recognize.recognize(temp)['cut_dict'][0]['label']
        except Exception:
            t = None
        return t

def getDataAndLink(res):
    data = []
    link = []
    name = []
    for path in res:
        # path = { 'node', 'rel' }
        # 获取节点
        for k in path['node']:
            # k = ['name', ['type']]
            k[0] = k[1][0] if k[0] == None else k[0]
            if k[0] not in name:
                name.append(k[0])
                r = {'name': k[0], 'symbolSize': 60, 'c': 1, 'type': k[1][0]}
                data.append(r)
        # 获取关系
        for j in path['rel']:
            j[0] = j[1][0] if j[0] == None else j[0]
            j[3] = j[4][0] if j[3] == None else j[3]
            r_ = {'source': j[0], 'label': j[2], 'target': j[3]}
            if r_ not in link:
                link.append(r_)
    return data, link

# 大学 -> 专业
def universitySpecial(university):
    conn = NEO4j_POOL.getConnect()
    num = 20
    # 根据大学名称获取id
    u_id = conn.run("""
        match (n:university) where n.name = "%s" return n.id
        """ % (university,)).data()[0]["n.id"]
    # 获取其下的20个专业
    cypher_ = ("""
        match (m:major) where m.fk_university_id = %d return m.name limit %d;
    """ % (int(u_id), num))
    major = conn.run(cypher_).data()
    data = []
    link = []
    data.append({ 'name': university, 'symbolSize': 60, 'c': 1, 'type': 'university' })
    for major_dict in major:
        data.append({ 'name': major_dict['m.name'], 'symbolSize': 60, 'c': 1, 'type': 'major' })
        link.append({'source': university, 'label': 'HAS', 'target': major_dict['m.name']})
    NEO4j_POOL.free(conn)
    return data, link


# 只有实体之一，无关系:
def onlyOneEntityQuery(entity, num):
    type = entityType(entity)
    if type == None:
        return [], [], type
    if type == 'university':
        data, link = universitySpecial(entity)
        return data, link, type
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [r] - (n) where m.name contains "%s" return [node in nodes(path) | [node.name, labels(node)]] as node, [rel in relationships(path) | [startNode(rel).name, labels(startNode(rel)), type(rel), endNode(rel).name, labels(endNode(rel))]] as rel limit %d;
    """ % (type, entity, num))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    data, link = getDataAndLink(res)
    return data, link, type

# 一个实体查询  有关系
def oneOptionAndOneEntityQuery(entity, option, num):
    type = entityType(entity)
    if type == None:
        return [], []
    if type == 'university' and option == 'HAS':
        return universitySpecial(entity)
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [r:%s] - (n) where m.name = "%s" return [node in nodes(path) | [node.name, labels(node)]] as node, [rel in relationships(path) | [startNode(rel).name, labels(startNode(rel)), type(rel), endNode(rel).name, labels(endNode(rel))]] as rel limit %d;
    """ % (type, option, entity, num))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)   

    return getDataAndLink(res)

# 两个实体查询  无关系
def twoEntityQuery(entity1, entity2, num):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    if type1 == None or type2 == None:
        return [], []
    # 查询
    cypher_ = ("""
        match path = shortestpath((m:%s) - [*1..4] - (n:%s)) where m.name contains "%s" and n.name contains "%s" and m.name <> n.name return [node in nodes(path) | [node.name, labels(node)]] as node, [rel in relationships(path) | [startNode(rel).name, labels(startNode(rel)), type(rel), endNode(rel).name, labels(endNode(rel))]] as rel limit 1;
    """ % (type1, type2, entity1, entity2))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)

    return getDataAndLink(res)

# 判断选定的大学和专业的关系
def canBack(university, major):
    conn = NEO4j_POOL.getConnect()
    university_id = conn.run("""
        match (n:university) where n.name = "%s" return n.id;
    """ % (university,)).data()[0]["n.id"]
    # major_u_id = conn.run("""
    #     match (n:major) where n.name = "%s" and n.fk_university_id = %d return n.fk_university_id;
    # """ % (major, )).data()[0]["n.fk_university_id"]
    major_u_id = conn.run("""
        match (n:major) where n.name = "%s" and n.fk_university_id = %d return n.fk_university_id;
    """ % (major, university_id)).data()
    NEO4j_POOL.free(conn)
    if len(major_u_id) == 0:
        # 没有关系
        return [], []
    else:
        # 有关系
        return [{ 'name': university, 'symbolSize': 60, 'c': 1, 'type': 'university' }, { 'name': major, 'symbolSize': 60, 'c': 1, 'type': 'major' }], [{'source': university, 'label': 'HAS', 'target': major}]

# 两个实体查询  有关系
def oneOptionAndtTwoEntityQuery(entity1, option, entity2):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    if type1 in ['university', 'major'] and type2 in ['university', 'major']:
        return canBack(entity1, entity2)
    if type1 == None or type2 == None:
        return [], []
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [*1..2] - (b:%s) where m.name contains "%s" and b.name contains "%s" and any(rel in relationships(path) where type(rel) = "%s") return [node in nodes(path) | [node.name, labels(node) ] ] as node, [rel in relationships(path) | [startNode(rel).name, labels(startNode(rel)), type(rel), endNode(rel).name, labels(endNode(rel))] ] as rel;
    """ % (type1, type2, entity1, entity2, option))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)

    return getDataAndLink(res)

# 获取某一省份下对应的年份信息
def yearsInfo(province_name):
    # 查询
    cypher_ = ("""
        match (n:fractional_line) - [:BELONG_TO] -> (m:province) where m.name = "%s" return n.year;
    """ % (province_name, ))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # dict_keys(['n.year'])
    return list(set([k['n.year'] for k in res])), province_list


def cateDegreeInfo(province_name, year):
    # 查询
    cypher_ = ("""
        MATCH (n:fractional_line) - [:BELONG_TO] -> (m:province) where m.name = "%s" and n.year = "%s" RETURN n.category, n.degree;
    """ % (province_name, year))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # dict_keys(['n.category', 'n.degree'])

    return list(set([r['n.category']
                     for r in res])), list(set([k['n.degree'] for k in res]))


def scoreInfo(province_name, year, category, degree):
    # 查询
    if degree == 'NoneType' or len(degree) == 0:
        degree = '不分层次'
    cypher_ = ("""
        match (n:fractional_line) - [:BELONG_TO] -> (m:province) where m.name = "%s" and n.year = "%s" and n.category = "%s" and n.degree = "%s" return n.detail;
    """ % (province_name, year, category, degree))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # dict_keys([0]['n.detail'])
    data = json.loads(res[0]['n.detail'])
    score = []
    keys = []
    data_detail = {}
    for k_ in data.keys():
        data_detail[int(k_.split('-')[0])] =  { k_: data[k_] }

    for key in sorted(data_detail, reverse=True):
        keys.append(list(data_detail[key].keys())[0])
        score.append(list(data_detail[key].values())[0])

    return score, keys
# 大学 -> 专业
def universitySpecial(university):
    print(university)
    conn = NEO4j_POOL.getConnect()
    num = 10
    # 根据大学名称获取id
    u_id = conn.run("""
        match (n:university) where n.name = "%s" return n.id
        """ % (university,)).data()[0]["n.id"]
    # 获取其下的10个专业
    cypher_ = ("""
        match (m:major) where m.fk_university_id = %d return m.name limit %d;
    """ % (int(u_id), num))
    major = conn.run(cypher_).data()
    data = []
    link = []
    data.append({ 'name': university, 'symbolSize': 60, 'c': 1, 'type': 'university' })
    if len(major) != 0:
        for major_dict in major:
            data.append({ 'name': major_dict['m.name'], 'symbolSize': 60, 'c': 1, 'type': 'major' })
            link.append({'source': university, 'label': 'HAS', 'target': major_dict['m.name']})
    NEO4j_POOL.free(conn)
    return data, link

# match (p:province) - [:REFER] -> (n:major_line) <- [:SET] - (m:major) where p.name = '安徽' and  n.year = '2022' and n.lowScore > '650' return m.name, m.ruanKeScore, m.fk_university_id, n.lowScore limit 5;
def ScoreRecommend(province, myScore):
    # 获取区间
    minScore = int(myScore) - 50
    if minScore < 0:
        minScore = 0
    province_id = province_id_dict[province]
    # 查询
    cypher_ = ("""
        match (n:major_line) <- [:SET] - (m:major) where n.fk_province_id = %d and  n.year = "2022" and not n.lowScore contains '-' and toInteger(split(n.lowScore, '/')[0]) < %d and toInteger(split(n.lowScore, '/')[0]) > %d return m.name, m.ruanKeScore, m.fk_university_id, n.lowScore;
    """ % (int(province_id), int(myScore), minScore))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    # 处理数据 返回 m.name, m.ruanKeScore, m.fk_university_id, n.lowScore
    universitys_id_name = {}
    for item_dict in res:
        item_dict["m.ruanKeScore"] = '暂无数据' if item_dict["m.ruanKeScore"] == '' else item_dict["m.ruanKeScore"]
        if item_dict["m.fk_university_id"] not in universitys_id_name:
            universitys_id_name[item_dict["m.fk_university_id"]] = item_dict["m.fk_university_id"]
    # 再次查询，获取对应大学的名称
    for i in universitys_id_name.keys():
        universitys_id_name[i] = conn.run("match (n:university) where n.id = %d return n.name" % (i,)).data()[0]["n.name"]
    # 添加 res[0] 中每个字典中id对应的名字
    for k in res:
        k['name'] = universitys_id_name[k['m.fk_university_id']]
    NEO4j_POOL.free(conn)
    # 按照 res 中的 lowScore降序排列
    res.sort(key = lambda t: t['n.lowScore'], reverse=True)

    return res

def RankRecommend(province, myRank):
    province_id = province_id_dict[province]
    # 查询
    cypher_ = ("""
        match (n:major_line) <- [:SET] - (m:major) where n.fk_province_id = %d and  n.year = "2022" and not n.lowScore contains '-' and toInteger(split(n.lowScore, '/')[1]) > %d return m.name, m.ruanKeScore, m.fk_university_id, n.lowScore;
    """ % (int(province_id), int(myRank)))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    # 处理数据 返回 m.name, m.ruanKeScore, m.fk_university_id, n.lowScore 
    universitys_id_name = {}
    for item_dict in res:
        item_dict["m.ruanKeScore"] = '暂无数据' if item_dict["m.ruanKeScore"] == '' else item_dict["m.ruanKeScore"]
        if item_dict["m.fk_university_id"] not in universitys_id_name:
            universitys_id_name[item_dict["m.fk_university_id"]] = item_dict["m.fk_university_id"]
    # 再次查询，获取对应大学的名称
    for i in universitys_id_name.keys():
        universitys_id_name[i] = conn.run("match (n:university) where n.id = %d return n.name" % (i,)).data()[0]["n.name"]
    # 添加 res[0] 中每个字典中id对应的名字
    for k in res:
        k['name'] = universitys_id_name[k['m.fk_university_id']]
    NEO4j_POOL.free(conn)
    # 按照 res 中的 lowScore降序排列
    res.sort(key = lambda t: t['n.lowScore'], reverse=True)

    return res


# 一个实体  一个标签类型  关系
def aiTwoEntityQuery(entity_name, entity_type, num, label):
    type1 = entityType(entity_name)
    print(type1)
    print(entity_type)
    print(entity_name)
    print(label)
    if type1 == None:
        return [], []
    # 查询
    cypher_ = ''
    if label == 'HAS':
        data, link = universitySpecial(entity_name)
        return universitySpecial(entity_name)
    elif label == 'RELATED_TO' or label == 'SET':
        cypher_ = ("""
            match p = (n:%s) - [*1..3] -> (m:%s) where n.name = "%s" and any(rel in relationships(p) where type(rel) = '%s')  return m.name limit 10;
        """ % (type1, entity_type, entity_name, label))
    else: 
        cypher_ = ("""
            match p = (n:%s) <- [*1..3] - (m:%s) where n.name = "%s" and any(rel in relationships(p) where type(rel) = '%s')  return m.name limit 10;
        """ % (type1, entity_type, entity_name, label))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    data = []
    link = []
    data.append({ 'name': entity_name, 'symbolSize': 60, 'c': 1, 'type': type1 })
    if len(res) != 0:
        for major_dict in res:
            data.append({ 'name': major_dict['m.name'], 'symbolSize': 60, 'c': 1, 'type': entity_type })
            link.append({'source': entity_name, 'label': label, 'target': major_dict['m.name']})
    NEO4j_POOL.free(conn)
    return data, link

# def getProAndUni(province, uni):
#     data, link = twoEntityQuery(province, uni, 10)
#     # 查询
#     cypher_ = ("""
#         match (m:university) where m.name = "%s" return m.intro;
#     """ % (uni))
#     conn = NEO4j_POOL.getConnect()
#     res = conn.run(cypher_).data()[0]['m.intro']
#     NEO4j_POOL.free(conn)
#     return data, link
#随即打乱数组
def RandomHot(hot):
    length=len(hot)
    temp = [i for i in range(length)]
    random.shuffle(temp)
    arr=[]
    for i in temp:
        arr.append(hot[i])
    return arr

#对数据库中大学专业进行识别并返回
def content(h,conn):
    # 连接
    res='暂无详情'
    if len(Recognize.recognize(h)['cut_dict'])==0:
        res='暂无详情'
    else:
        if Recognize.recognize(h)['cut_dict'][0]['label']=='university':
            cypher = ("""
            match (n:university) where n.name = "%s" return n.intro
            """ % (h))
            res = conn.run(cypher).data()[0]['n.intro']
        elif Recognize.recognize(h)['cut_dict'][0]['label']=='major':
            cypher = ("""
            match (n:major) where n.name = "%s" return n.detail limit 1
            """ % (h))
            res = conn.run(cypher).data()[0]['n.detail']
        if res[0] == '[':
            res = json.loads(res)
            res = ''.join(res)
        res = res.replace('\n','').replace('\t','').replace('<p>','').replace('<a>','').replace('\r','').replace('</p>', '').replace('</a>', '').replace('<strong>','').replace('</strong>','').replace('</br>','')
    return res
