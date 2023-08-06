import json
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

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
            }
        finally:
            NEO4j_POOL.free(conn)
        return JsonResponse({"status": True, "data": data})
    elif label == "major":
        conn = NEO4j_POOL.getConnect()
        try:
            cursor = conn.run(
                cypher="match (a: %s) where a.name=$name return a" % label,
                params={"name": name},
            )
            data = cursor.data()[0]["a"]
            cursor = conn.run(
                cypher=
                "match (a: %s)<-[r:HAS]-(b:university) where a.name=$name return r, b limit 5"
                % label,
                params={"name": name},
            )
            rel = cursor.data()
            data = {
                "name": data["name"],
                "mainBranch": data["mainBranch"],
                "subBranch": data["subBranch"],
                "duration": data["duration"],
                "careerInfo": data["careerInfo"],
                "relation": rel,
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
                    "match (a: %s)-[:BELONG_TO]->(b:university) where a.name=$name return b"
                    % label,
                    params={"name": name},
                )
                university = cursor.data()[0]["b"]
                cursor = conn.run(
                    cypher=
                    "match (a: %s)-[:BELONG_TO]->(b:university) where b.name=$name return a.name, a.identity limit 5"
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
