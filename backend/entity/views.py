from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

from neo4j_model.db_pool import NEO4j_POOL



def index(request):
    return HttpResponse("hello")


@require_http_methods(["GET"])
def query(request):
    entity = request.GET.get("entity", None)
    label = request.GET.get("label", None)
    if entity is None or label is None:
        return JsonResponse({"status": False, "error": "查无该实体"})
    conn = NEO4j_POOL.getConnect()
