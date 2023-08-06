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
def onlyOneEntityQuery(entity):
    type = entityType(entity)
    data = []
    link = []
    data.append({ 'name': entity, 'symbolSize': 30, 'type': type })
    # 查询
    cypher_ = ("""
        match (m:%s) - [r] - (b) where m.name = "%s" return m.name, type(r), b limit 25;
    """ % (type, entity))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # 获取数据
    for i in res:
        # name是字符串   type是列表
        r = {'name': i['b']['name'], 'symbolSize': 30, 'type': ",".join(list(i['b'].labels)) }
        data.append(r)
    # 获取关系
    for k in res:
        r_ = { 'source': k['m.name'], 'label': k['type(r)'], 'target': k['b']['name'] }
        link.append(r_)
    return data, link

# 只有实体之一，有关系
def oneOptionAndOneEntityQuery(entity, option):
    type = entityType(entity)
    data = []
    link = []
    data.append({ 'name': entity, 'symbolSize': 30, 'type': type })
    # 查询
    cypher_ = ("""
        match (m:%s) - [r:%s] - (b) where m.name = "%s" return m.name, b limit 25;
    """ % (type, option, entity))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # 获取数据
    for i in res:
        # name是字符串   type是列表
        r = {'name': i['b']['name'], 'symbolSize': 30, 'type': ",".join(list(i['b'].labels)) }
        data.append(r)
    # 获取关系
    for k in res:
        r_ = { 'source': k['m.name'], 'label': option, 'target': k['b']['name'] }
        link.append(r_)
    return data, link

# 两个实体查询  无关系
def twoEntityQuery(entity1, entity2):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    data = []
    link = []
    # 查询
    cypher_ = ("""
        match path = (m:%s) - [*..5] - (n:%s) where m.name in ["%s", "%s"] and n.name in ["%s", "%s"] and m.name<>n.name return [node in nodes(path) | [node.name, labels(node) ] ] as node, [rel in relationships(path) | [startNode(rel).name, type(rel), endNode(rel).name] ] as rel limit 10;
    """ % (type1, type2, entity1, entity2, entity1, entity2))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    name = []
    for path in res:
        # path = { 'node', 'rel' }
        # 获取节点
        for k in path['node']:
            # k = ['name', ['type']]
            if k[0] not in name:
                name.append(k[0])
                r = {'name': k[0], 'symbolSize': 30, 'type': k[1][0] }
                data.append(r)
        # 获取关系
        for j in path['rel']:
            r_ = { 'source': j[0], 'label': j[1], 'target': j[2] }
            link.append(r_)
    return data, link

# 两个实体查询  有关系
def oneOptionAndtTwoEntityQuery(entity1, option, entity2):
    type1 = entityType(entity1)
    type2 = entityType(entity2)
    data = []
    link = []
    data.append({ 'name': entity1, 'symbolSize': 30, 'type': type1 })
    data.append({ 'name': entity2, 'symbolSize': 30, 'type': type2 })
    # 查询
    cypher_ = ("""
        match (m:%s) - [r:%s] - (b:%s) where m.name = "%s" and b.name = "%s" return m.name, b limit 25;
    """ % (type1, option, type2, entity1, entity2))
    conn = NEO4j_POOL.getConnect()
    res = conn.run(cypher_).data()
    NEO4j_POOL.free(conn)
    # 获取数据
    for i in res:
        # name是字符串   type是列表
        r = {'name': i['b']['name'], 'symbolSize': 30, 'type': ",".join(list(i['b'].labels)) }
        data.append(r)
    # 获取关系
    for k in res:
        r_ = { 'source': k['m.name'], 'label': option, 'target': k['b']['name'] }
        link.append(r_)
    return data, link