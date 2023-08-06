from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

from neo4j_model.db_pool import NEO4j_POOL
from py2neo import Graph
import json
import entity.neo4j as neo4j

def index(request):
    return HttpResponse("hello")

@require_http_methods(["GET"])
def query(request):
    entity = request.GET.get("entity", None)
    label = request.GET.get("label", None)
    if entity is None or label is None:
        return JsonResponse({"status": False, "error": "查无该实体"})
    conn = NEO4j_POOL.getConnect()

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