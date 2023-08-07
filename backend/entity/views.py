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
                cypher="match (a)-[:BELONG_TO]->(s)-[:BELONG_TO]->(m)<-[:HAS]-(b:%s) where b.name=$name and a.fk_university_id=b.id return a, b.name, s.name, m.name"
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
                name = r["m.name"] + "(" + r["b.name"] + ")"
                if name not in major_get:
                    rel.append({"name": name, "symbolSize": 30, "c": 0})
                    link.append({"source": name, "label": "属于", "target": r["b.name"]})
                    major_get.append(name)
                if r["b.name"] not in main_get:
                    rel.append({"name": r["b.name"], "symbolSize": 30, "c": 1})
                    main_get.append(r["b.name"])
            major_get = []
            for r in result:
                main_name = r["m.name"]
                if recommend.get(main_name, None) is None:
                    recommend[main_name] = []
                if main_name + r["a"]["name"] not in major_get:
                    recommend[main_name].append(
                        {
                            "main_branch": r["m.name"],
                            "sub_branch": r["s.name"],
                            "name": r["a"]["name"],
                        }
                    )
                    major_get.append(main_name + r["a"]["name"])
            cursor = conn.run(
                cypher="match (a:living_condition)<-[:HAS]-(b:%s) where b.name=$name return a"
                % label,
                params={"name": name},
            )
            living_condition = cursor.data()
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
                "living_condition": living_condition
            }
        finally:
            NEO4j_POOL.free(conn)
        return JsonResponse({"status": True, "data": data})
    elif label == "major":
        conn = NEO4j_POOL.getConnect()
        try:
            cursor = conn.run(
                cypher="match (a: %s)-[:BELONG_TO]->(s:sub_branch)-[:BELONG_TO]->(m:main_branch) where a.name=$name return a, s.name, m.name"
                % label,
                params={"name": name},
            )
            data = cursor.data()[0]
            cursor = conn.run(
                cypher="match (a:%s)-[:BELONG_TO]->(s)-[:BELONG_TO]->(m)<-[:HAS]-(b:university) where a.name contains($name) and a.fk_university_id=b.id return a, b.name, s.name, m.name limit 100"
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
                    rel.append({"name": name, "symbolSize": 30, "c": 0})
                    link.append({"source": name, "label": "属于", "target": r["b.name"]})
                    major_get.append(name)
                if r["b.name"] not in uni_get:
                    rel.append({"name": r["b.name"], "symbolSize": 30, "c": 1})
                    uni_get.append(r["b.name"])
                else:
                    limit += 1
            major_get = []
            for r in result:
                uni_name = r["b.name"]
                if recommend.get(uni_name, None) is None:
                    recommend[uni_name] = []
                if uni_name + r["a"]["name"] not in major_get:
                    recommend[uni_name].append(
                        {
                            "main_branch": r["m.name"],
                            "sub_branch": r["s.name"],
                            "name": r["a"]["name"],
                        }
                    )
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
            result["infoDict"] = (
                result["infoDict"] if result["infoDict"] is not None else "{}"
            )
            data = {
                "name": result["name"],
                "tag": result["tag"],
                "infoDict": json.loads(result["infoDict"]),
                "intro": result["intro"],
            }
            if label == "person":
                data["identity"] = result["identity"]
                cursor = conn.run(
                    cypher="match (a: %s)-[]->(b:university) where a.name=$name return b"
                    % label,
                    params={"name": name},
                )
                university = cursor.data()[0]["b"]
                cursor = conn.run(
                    cypher="match (a: %s)-[]->(b:university) where b.name=$name return a.name, a.identity limit 5"
                    % label,
                    params={"name": university["name"]},
                )
                related = cursor.data()
                related = [
                    {"name": person["a.name"], "identity": person["a.identity"]}
                    for person in related
                ]
                data["university"] = university
                data["related"] = related
            else:
                cursor = conn.run(
                    cypher="match (a: %s) where a.name<>$name return a.name limit 5"
                    % label,
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
    # 共有三种类型  大学、专业、省份、城市
    entity1 = request.GET.get('entity1', None)
    option = request.GET.get('option', None)
    entity2 = request.GET.get('entity2', None)
    data = []
    link = []
    # 至少一个实体
    if len(entity1) == 0 and len(entity2) == 0:
        return JsonResponse('请先输入一个实体！')
    # 情况1：只有1个实体
    elif len(entity1) == 0 or len(entity2) == 0:
        entity = entity1 if len(entity2) == 0 else entity2
        # 未选择关系
        if len(option) == 0:
            data, link = neo4j.onlyOneEntityQuery(entity)
        # 选择关系
        else:
            data, link = neo4j.oneOptionAndOneEntityQuery(entity, option)
        d_ = { 'data': data, 'link': link }
        return JsonResponse(json.dumps(d_), safe=False)
    # 情况2：2个实体
    else:
        # 未选择关系
        if len(option) == 0:
            data, link = neo4j.twoEntityQuery(entity1, entity2)
        # 选择关系
        else:
            data, link = neo4j.oneOptionAndtTwoEntityQuery(entity1, option, entity2)
        d_ = { 'data': data, 'link': link }
        return JsonResponse(json.dumps(d_), safe=False)
    
@require_http_methods(["GET"])
def IntelligentQuery(request):
    entity = request.GET.get("entity", None)
    if entity is None:
        return JsonResponse({ "error": "输入错误请重试"})
    entityGroup=Recognize.recognize(entity)
    for key in entityGroup['cut_dict']:
        data, link = neo4j.onlyOneEntityQuery(entityGroup['cut_dict'][key]['name'])
    d_ = { 'data': data, 'link': link }
    return JsonResponse(json.dumps(d_), safe=False)
