from neo4j_model.db_pool import NEO4j_POOL
import json
from py2neo import Relationship

# 获取所有省、市、大学、祖专业、父专业、专业的四个列表


def get_list(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        info_json = f.read()
    info = json.loads(info_json)
    list = []
    for i in info:
        list.append(i['n.name'])
    return list


province_list = get_list('entity/data/province.json')
city_list = get_list('entity/data/city.json')
university_list = get_list('entity/data/university.json')
major_list = get_list('entity/data/major.json')


def entityType(temp):
    if temp in province_list:
        return 'province'
    elif temp in city_list:
        return 'city'
    elif temp in university_list:
        return 'university'
    else:
        return 'major'


# 只有实体之一，无关系:
def onlyOneEntityQuery(entity, num):
    type = entityType(entity)
    data = []
    link = []
    data.append({'name': entity, 'symbolSize': 30, 'type': type, 'c': 2})
    # 查询
    cypher_ = ("""
        match (m:%s) - [r] - (b) where m.name contains "%s" return m.name, type(r), b limit %d;
    """ % (type, entity, num))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # 获取数据
    for i in res:
        # name是字符串   type是列表
        if i['b']['name'] != None:
            r = {
                'name': i['b']['name'],
                'symbolSize': 60,
                'type': ",".join(list(i['b'].labels)),
                'c': 1
            }
            data.append(r)
    # 获取关系
    for k in res:
        r_ = {
            'source': k['m.name'],
            'label': k['type(r)'],
            'target': k['b']['name']
        }
        link.append(r_)
    return data, link


# 只有实体之一，有关系
def oneOptionAndOneEntityQuery(entity, option, num):
    type = entityType(entity)
    data = []
    link = []
    data.append({'name': entity, 'symbolSize': 30, 'type': type})
    # 查询
    cypher_ = ("""
        match (m:%s) - [r:%s] - (b) where m.name contains "%s" return m.name, b limit %d;
    """ % (type, option, entity, num))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # 获取数据
    for i in res:
        # name是字符串   type是列表
        r = {
            'name': i['b']['name'],
            'symbolSize': 30,
            'c': 1,
            'type': ",".join(list(i['b'].labels))
        }
        data.append(r)
    # 获取关系
    for k in res:
        r_ = {'source': k['m.name'], 'label': option, 'target': k['b']['name']}
        link.append(r_)
    return data, link


# 两个实体查询  无关系
def twoEntityQuery(entity1, entity2, num):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    data = []
    link = []
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [*..5] - (n:%s) where m.name in ["%s", "%s"] and n.name in ["%s", "%s"] and m.name<>n.name return [node in nodes(path) | [node.name, labels(node) ] ] as node, [rel in relationships(path) | [startNode(rel).name, type(rel), endNode(rel).name] ] as rel limit %d;
    """ % (type1, type2, entity1, entity2, entity1, entity2, num))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)

    name = []
    for path in res:
        # path = { 'node', 'rel' }
        # 获取节点
        for k in path['node']:
            # k = ['name', ['type']]
            if k[0] not in name and k[0] != None:
                name.append(k[0])
                r = {'name': k[0], 'symbolSize': 30, 'c': 1, 'type': k[1][0]}
                data.append(r)
        # 获取关系
        for j in path['rel']:
            r_ = {'source': j[0], 'label': j[1], 'target': j[2]}
            link.append(r_)
    return data, link


# 两个实体查询  有关系
def oneOptionAndtTwoEntityQuery(entity1, option, entity2):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    data = []
    link = []
    data.append({'name': entity1, 'symbolSize': 30, 'type': type1})
    data.append({'name': entity2, 'symbolSize': 30, 'type': type2})
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [*1..3] - (b:%s) where m.name contains "%s" and b.name contains "%s" and any(rel in relationships(path) where type(rel) = "%s") return [node in nodes(path) | [node.name, labels(node) ] ] as node, [rel in relationships(path) | [startNode(rel).name, type(rel), endNode(rel).name] ] as rel;
    """ % (type1, type2, entity1, entity2, option))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    name = []
    for path in res:
        # path = { 'node', 'rel' }
        # 获取节点
        for k in path['node']:
            # k = ['name', ['type']]
            if k[0] not in name and k[0] != None:
                name.append(k[0])
                r = {'name': k[0], 'symbolSize': 30, 'c': 1, 'type': k[1][0]}
                data.append(r)
        # 获取关系
        for j in path['rel']:
            r_ = {'source': j[0], 'label': j[1], 'target': j[2]}
            link.append(r_)

    return data, link


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
    print(province_name)
    print(year)
    print(category)
    print(degree)
    if degree == 'NoneType' or len(degree) == 0:
        degree = '不分层次'
    cypher_ = ("""
        MATCH (n:fractional_line) - [:BELONG_TO] -> (m:province) WHERE m.name = "%s" AND n.year = "%s" AND n.category = "%s" AND n.degree = "%s" RETURN n.detail;
    """ % (province_name, year, category, degree))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # dict_keys([0]['n.detail'])
    print(res)
    data = json.loads(res[0]['n.detail'])
    score = []
    for key in sorted(data):
        score.append(data[key])

    return score, sorted(data)