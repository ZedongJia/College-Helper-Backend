import json
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

from neo4j_model.db_pool import NEO4j_POOL
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
