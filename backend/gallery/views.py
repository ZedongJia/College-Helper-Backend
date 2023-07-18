from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.db import connection, Error

# Create your views here.
@require_http_methods(['GET'])
def match(request):
    ID = request.GET.get('ID', None)
    with open('static/test.png', 'rb') as r:
        image = r.read()
    return HttpResponse(image, content_type='image/png')