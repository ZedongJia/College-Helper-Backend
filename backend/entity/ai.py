from neo4j_model.db_pool import NEO4j_POOL
import json

def onlyOneEnity(nameAndLabel):
    conn = NEO4j_POOL.getConnect()
    relationList = []
    data = []
    link = []
    num = 10
    if nameAndLabel['label'] in ['city', 'province']:
        # 获取 地区-大学 关系模板：{安徽} 有 {安徽大学}、{合肥工业大学}等多所大学。
        relationList.append('考生想了解' + nameAndLabel['name'] + '有哪些大学，我将给你一些信息参考，请你在此基础上回答。')
        cypher_ = """
            match (n:%s) <- [*1..3] - (m:university) where n.name = "%s"  return m.name limit %d;
        """ % (nameAndLabel['label'], nameAndLabel['name'], num)
        u_ = conn.run(cypher_).data()
        data.append({ 'name': nameAndLabel['name'], 'symbolSize': 60, 'c': 1, 'type': nameAndLabel['label'] })
        for item_dict in u_:
            data.append({ 'name': item_dict['m.name'], 'symbolSize': 60, 'c': 1, 'type': 'university' })
            link.append({'source': nameAndLabel['name'], 'label': 'HAS', 'target': item_dict['m.name']})
            relationList.append(nameAndLabel['name'] + '拥有' + item_dict['m.name'])
        return data, link, relationList
    elif nameAndLabel['label'] == 'major':
        relationList.append('考生想了解' + nameAndLabel['name'] + '的相关信息，我将给你一些信息参考，请你在此基础上回答。')
        cypher_ = """
            match (m:major) return m.detail where m.name = "%s" limit %d;
        """ % (nameAndLabel['name'], num)
        u_ = conn.run(cypher_).data()
        data.append({ 'name': nameAndLabel['name'], 'symbolSize': 60, 'c': 1, 'type': nameAndLabel['label'] })
        relationList.append(nameAndLabel['name'] + '，简介：' + u_[0]['m.detail'] + '。帮我100字总结')
        return data, [], relationList
    elif nameAndLabel['label'] in ['person', 'university']:
        relationList.append('考生想了解' + nameAndLabel['name'] + '的相关信息，我将给你一些信息参考，请你在此基础上回答。')
        cypher_ = """
            match (m:%s) return m.intro where m.name = "%s" limit %d;
        """ % (nameAndLabel['label'], nameAndLabel['name'], num)
        u_ = conn.run(cypher_).data()
        data.append({ 'name': nameAndLabel['name'], 'symbolSize': 60, 'c': 1, 'type': nameAndLabel['label'] })
        relationList.append(nameAndLabel['name'] + '，简介：' + u_[0]['m.detail'] + '。帮我100字总结')
        return data, [], relationList
    else:
        return [], [], []