import json
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
import random
from neo4j_model.db_pool import NEO4j_POOL
from py2neo import Graph
import json
import entity.neo4j as neo4j
from models.recognize import Recognize


def index(request):
    return HttpResponse("hello")


def typeColar(type):
    if type == 'university':
        return 0
    elif type == 'city':
        return 1
    elif type == 'province':
        return 2
    elif type == 'living_condition':
        return 3
    elif type == 'main_branch':
        return 4
    elif type == 'major':
        return 5
    elif type.find('person') >= 0:
        return 6
    elif type == 'major_line':
        return 7
    elif type == 'total_line':
        return 8
    elif type == 'sub_branch':
        return 9
    elif type == 'fractional_line':
        return 10
    elif type.find('policy') >= 0:
        return 11
    return 0


@require_http_methods(["POST"])
def cut_sentence(request):
    sentence = request.POST.get("sentence", None)
    if sentence is None:
        return JsonResponse({"status": False, "error": "输入错误请重试"})
    cut_result = Recognize.recognize(sentence)
    return JsonResponse({"status": True, "cut_result": cut_result})


@require_http_methods(["GET"])
def queryEntity(request):
    name = request.GET.get("name", None)
    label = request.GET.get("label", None)
    if name is None or label is None:
        return JsonResponse({"status": False, "error": "查无该实体"})
    if label == "university":
        conn = NEO4j_POOL.getConnect()
        try:
            cursor = conn.run(
                cypher="match (a: %s) where a.name=$name return a" % label,
                params={"name": name},
            )
            data = cursor.data()[0]["a"]
            cursor = conn.run(
                cypher=
                "match (a:major)-[:BELONG_TO]->(s:sub_branch)-[:BELONG_TO]->(m:main_branch)<-[:HAS]-(b:%s) where b.name=$name and a.fk_university_id=b.id return a, b.name, s.name, m.name"
                % label,
                params={"name": name},
            )
            result = cursor.data()
            # process rel
            rel = []
            main_get = []
            major_get = []
            link = []
            recommend = {}
            for i, r in enumerate(result):
                m_name = r["m.name"]
                if m_name not in major_get:
                    rel.append({"name": m_name, "symbolSize": 60, "c": 0})
                    link.append({
                        "source": m_name,
                        "label": "属于",
                        "target": r["b.name"]
                    })
                    major_get.append(m_name)
                if r["b.name"] not in main_get:
                    rel.append({"name": r["b.name"], "symbolSize": 60, "c": 1})
                    main_get.append(r["b.name"])
            major_get = []
            for r in result:
                main_name = r["m.name"]
                if recommend.get(main_name, None) is None:
                    recommend[main_name] = []
                if main_name + r["a"]["name"] not in major_get:
                    recommend[main_name].append({
                        "main_branch": r["m.name"],
                        "sub_branch": r["s.name"],
                        "name": r["a"]["name"],
                    })
                    major_get.append(main_name + r["a"]["name"])
            cursor = conn.run(
                cypher=
                "match (a:living_condition)-[:BELONG_TO]->(b:%s) where b.name=$name return a"
                % label,
                params={"name": name},
            )
            living_condition = cursor.data()
            living_condition = [c["a"] for c in living_condition]
            data = {
                "name": data["name"],
                "establishTime": data["establishTime"],
                "honorTags": json.loads(data["honorTags"]),
                "imageUrls": json.loads(data["imageUrls"]),
                "officialPhoneNumber": json.loads(data["officialPhoneNumber"]),
                "officialWebsite": json.loads(data["officialWebsite"]),
                "officialEmail": data["officialEmail"],
                "intro": json.loads(data["intro"]),
                "rankInfo": json.loads(data["rankInfo"]),
                "educationInfo": json.loads(data["educationInfo"]),
                "related": rel,
                "link": link,
                "recommend": recommend,
                "living_condition": living_condition,
            }
        finally:
            NEO4j_POOL.free(conn)
        return JsonResponse({"status": True, "data": data})
    elif label == "major":
        conn = NEO4j_POOL.getConnect()
        try:
            cursor = conn.run(
                cypher=
                "match (a: %s)-[:BELONG_TO]->(s:sub_branch)-[:BELONG_TO]->(m:main_branch) where a.name=$name return a, s.name, m.name"
                % label,
                params={"name": name},
            )
            data = cursor.data()[0]
            cursor = conn.run(
                cypher=
                "match (a:%s)-[:BELONG_TO]->(s:sub_branch)-[:BELONG_TO]->(m:main_branch)<-[:HAS]-(b:university) where a.name contains($name) and a.fk_university_id=b.id return a, b.name, s.name, m.name limit 300"
                % label,
                params={"name": name},
            )
            result = random.choices(cursor.data(), k=30)
            # process rel
            limit = 5
            rel = []
            uni_get = []
            major_get = []
            link = []
            recommend = {}
            for i, r in enumerate(result):
                if i >= limit:
                    break
                name = r["a"]["name"] + "(" + r["b.name"] + ")"
                if name not in major_get:
                    rel.append({"name": name, "symbolSize": 60, "c": 0})
                    link.append({
                        "source": name,
                        "label": "属于",
                        "target": r["b.name"]
                    })
                    major_get.append(name)
                if r["b.name"] not in uni_get:
                    rel.append({"name": r["b.name"], "symbolSize": 60, "c": 1})
                    uni_get.append(r["b.name"])
                else:
                    limit += 1
            major_get = []
            for r in result:
                uni_name = r["b.name"]
                if recommend.get(uni_name, None) is None:
                    recommend[uni_name] = []
                if uni_name + r["a"]["name"] not in major_get:
                    recommend[uni_name].append({
                        "main_branch": r["m.name"],
                        "sub_branch": r["s.name"],
                        "name": r["a"]["name"],
                    })
                    major_get.append(uni_name + r["a"]["name"])
            # process recommend
            data = {
                "name": data["a"]["name"],
                "mainBranch": data["m.name"],
                "subBranch": data["s.name"],
                "duration": data["a"]["duration"],
                "careerInfo": data["a"]["careerInfo"],
                "related": rel,
                "link": link,
                "recommend": recommend,
            }
        finally:
            NEO4j_POOL.free(conn)
        return JsonResponse({"status": True, "data": data})
    else:
        conn = NEO4j_POOL.getConnect()
        try:
            cursor = conn.run(
                cypher="match (a: %s) where a.name=$name return a" % label,
                params={"name": name},
            )
            result = cursor.data()[0]["a"]
            result["infoDict"] = (result["infoDict"]
                                  if result["infoDict"] is not None else "{}")
            data = {
                "name": result["name"],
                "tag": result["tag"],
                "infoDict": json.loads(result["infoDict"]),
                "intro": result["intro"],
            }
            if label == "person":
                data["identity"] = result["identity"]
                cursor = conn.run(
                    cypher=
                    "match (a: %s)-[]->(b:university) where a.name=$name return b"
                    % label,
                    params={"name": name},
                )
                university = cursor.data()[0]["b"]
                cursor = conn.run(
                    cypher=
                    "match (a: %s)-[]->(b:university) where b.name=$name return a.name, a.identity limit 5"
                    % label,
                    params={"name": university["name"]},
                )
                related = cursor.data()
                related = [{
                    "name": person["a.name"],
                    "identity": person["a.identity"]
                } for person in related]
                data["university"] = university
                data["related"] = related
            else:
                cursor = conn.run(
                    cypher=
                    "match (a: %s) where a.name<>$name return a.name limit 5" %
                    label,
                    params={"name": name},
                )
                related = cursor.data()
                related = [{"name": person["a.name"]} for person in related]
                data["related"] = related
        finally:
            NEO4j_POOL.free(conn)
        return JsonResponse({"status": True, "data": data})


@require_http_methods(["GET"])
def RelationQuery(request):
    entity1 = request.GET.get("entity1", None)
    option = request.GET.get("option", None)
    entity2 = request.GET.get("entity2", None)
    print(option)
    data = []
    link = []
    # 至少一个实体
    if len(entity1) == 0 and len(entity2) == 0:
        return JsonResponse("请先输入一个实体！")
    # 情况1：只有1个实体
    elif len(entity1) == 0 or len(entity2) == 0:
        entity = entity1 if len(entity2) == 0 else entity2
        # 未选择关系
        if len(option) == 0:
            data, link, type = neo4j.onlyOneEntityQuery(entity, 25)
        # 选择关系
        else:
            data, link = neo4j.oneOptionAndOneEntityQuery(entity, option, 25)
    # 情况2：2个实体
    else:
        # 未选择关系
        if len(option) == 0 or option == None:
            data, link = neo4j.twoEntityQuery(entity1, entity2, 1)
        # 选择关系
        else:
            data, link = neo4j.oneOptionAndtTwoEntityQuery(
                entity1, option, entity2)
    d_ = {"data": data, "link": link}
    for d in d_['data']:
        d['c'] = typeColar(d['type'])
    return JsonResponse(json.dumps(d_), safe=False)

@require_http_methods(["GET"])
def IntelligentQuery(request):
    entity = request.GET.get("entity", None)
    if entity is None:
        return JsonResponse({"error": "输入错误请重试"})
    entityGroup = Recognize.recognize(entity)
    #分词数量
    length = len(entityGroup['cut_dict'])
    #返回节点数量
    num = 30 - length * 5 if (30 - length * 5 > 0) else 1
    #初始化data,link
    data = []
    relation_link = []
    entity_link = []
    # 节点名字
    data_name = []
    for key in entityGroup['cut_dict']:
        print(3, entityGroup['cut_dict'][key]['name'])
        temp_data, temp_link, type = neo4j.onlyOneEntityQuery(
            entityGroup['cut_dict'][key]['name'], num)
        entity_link.append({
            'name': entityGroup['cut_dict'][key]['name'],
            'type': type
        })
        for d in temp_data:
            if d not in data:
                data.append(d)
                data_name.append(d['name'])
        for l in temp_link:
            if l not in relation_link:
                if l['source'] in data_name:
                    relation_link.append(l)
    d_ = {
        'data': data,
        'relation_link': relation_link,
        'entity_link': entity_link
    }
    for d in d_['data']:
        d['c'] = typeColar(d['type'])
    return JsonResponse(json.dumps(d_), safe=False)


# 获取某一省的全部信息
# 必选参数：province_name
# 返回值：allCondition[ {所有省份}, {所选省份的所有年份}, { {所选省份的对应年份--所有专业类别、所有学生类别} } ]

# r"""
# 点击省份时
# 先获取该省份的所有年份信息返回，
# 再默认获取第一个年份对应的 category 与 degree,
# 再默认获取第一个 category 与 degree 对应的一分一段
# """

# 参数：provinceName
@require_http_methods(["GET"])
def getProYearsInfo(request):
    province_name = request.GET.get("provinceName", None)
    province = neo4j.province_list
    # 获取年份信息
    years, province = neo4j.yearsInfo(province_name)
    not_exists = ['新疆', '香港', '澳门', '台湾', '西藏']
    for k in not_exists:
        if k in province:
            province.remove(k)
    return JsonResponse(json.dumps({
        "years": years,
        "province": province
    }),
                        safe=False)


# 参数：provinceName， year
@require_http_methods(["GET"])
def getCateDegreeInfo(request):
    province_name = request.GET.get("provinceName", None)
    year = request.GET.get("year", None)
    # 获取 category 与 degree 信息
    category, degree = neo4j.cateDegreeInfo(province_name, year)
    return JsonResponse(json.dumps({
        "category": category,
        "degree": degree
    }),
                        safe=False)

# 参数：provinceName, year, category, (degree)
@require_http_methods(["GET"])
def getScoreInfo(request):
    province_name = request.GET.get("provinceName", None)
    year = request.GET.get("year", None)
    category = request.GET.get("category", None)
    degree = request.GET.get("degree", None)
    # 获取 detail 信息
    detail, keys = neo4j.scoreInfo(province_name, year, category, degree)
    print(keys)
    return JsonResponse({
        "detail": detail,
        'keys': keys
    }, safe=False)


@require_http_methods(["GET"])
def ScoreRecommend(request):
    province_name = request.GET.get("provinceName", None)
    myScore = request.GET.get("myScore", None)
    # 获取 detail 信息
    detail_dict = neo4j.ScoreRecommend(province_name, myScore)
    # 加工  全部传到前端
    # title: university_name
    # content: '专业名称：' + item_dict['m.name'] + '\n' + '专业排名：' + item_dict['m.ruanKeScore'] + '\n'
    #           + '往年最低录取分数/排名：' + item_dict['n.lowScore']
    # link: 大学或专业 对应的详情界面
    data = []
    print(detail_dict)
    num = 0
    for item_dict in detail_dict:
        content = '专业名称：<a>' + item_dict['m.name'] + '</a>\n' + '专业排名：' + item_dict['m.ruanKeScore'] + '\n' + '往年最低录取分数/排名：' + item_dict['n.lowScore']
        link = 'http://localhost:8080/#/system/identification/detailContent?name=' +  item_dict["name"] +  '&label=university'
        data.append({ 'title': item_dict["name"], 'content': content, 'link': link })
        num += 1
        if num == 20:
            break

    return JsonResponse(json.dumps(data), safe=False)